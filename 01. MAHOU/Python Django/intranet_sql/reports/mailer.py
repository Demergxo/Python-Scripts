"""Provider adapters. Never automatically retry an ambiguous submission."""

import base64
import smtplib
import socket
import ssl
from pathlib import Path
from urllib.parse import quote
import msal
import requests
from django.conf import settings
from django.core.mail import EmailMessage
from .artifacts import artifact


class MailFailure(Exception):
    def __init__(self, message, kind="failed", delay=300):
        super().__init__(message)
        self.kind = kind
        self.delay = delay


def build_message(delivery):
    job = delivery.job
    path = artifact(job, job.output_format)
    if not path.exists():
        raise MailFailure("No se encuentra el archivo generado.")
    if path.stat().st_size > settings.MAIL_MAX_ATTACHMENT_BYTES:
        raise MailFailure(
            "Adjunto supera MAIL_MAX_ATTACHMENT_BYTES. Descárgalo en la web o reduce el periodo."
        )
    msg = EmailMessage(
        subject=job.subject,
        body=job.body,
        from_email=settings.MAIL_FROM,
        to=[delivery.recipient],
        headers={"X-Intranet-Delivery": str(delivery.pk)},
    )
    msg.attach_file(path)
    return msg, path


def smtp_send(msg):
    if not settings.SMTP_HOST:
        raise MailFailure("Falta SMTP_HOST.")
    if settings.SMTP_SSL and settings.SMTP_TLS:
        raise MailFailure("Usa SMTP_SSL o SMTP_TLS, no ambos.")
    server = None
    phase = "connect"
    try:
        klass = smtplib.SMTP_SSL if settings.SMTP_SSL else smtplib.SMTP
        server = klass(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30)
        if settings.SMTP_TLS:
            server.starttls(context=ssl.create_default_context())
        if settings.SMTP_USER:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        phase = "submit"
        refused = server.sendmail(msg.from_email, msg.to, msg.message().as_bytes())
        if refused:
            raise MailFailure("Destinatario rechazado por SMTP.")
    except smtplib.SMTPRecipientsRefused as e:
        code = next(iter(e.recipients.values()))[0]
        raise MailFailure(
            f"SMTP rechazó destinatario ({code}).",
            "retry" if 400 <= code < 500 else "failed",
        ) from e
    except smtplib.SMTPResponseException as e:
        raise MailFailure(
            f"Error SMTP ({e.smtp_code}).",
            "retry" if 400 <= e.smtp_code < 500 else "failed",
        ) from e
    except (OSError, smtplib.SMTPServerDisconnected) as e:
        raise MailFailure(
            "Conexión SMTP interrumpida.", "uncertain" if phase == "submit" else "retry"
        ) from e
    except smtplib.SMTPException as e:
        raise MailFailure(
            "Error del protocolo SMTP.", "uncertain" if phase == "submit" else "failed"
        ) from e
    finally:
        if server is not None:
            # sendmail already knows acceptance; QUIT failure must not change its outcome.
            try:
                server.close()
            except OSError:
                pass


def graph_send(delivery, path):
    if not all(
        [
            settings.GRAPH_TENANT_ID,
            settings.GRAPH_CLIENT_ID,
            settings.GRAPH_CLIENT_SECRET,
            settings.GRAPH_SENDER,
        ]
    ):
        raise MailFailure("Falta configuración GRAPH_*.")
    if path.stat().st_size > 2_000_000:
        raise MailFailure(
            "Graph: esta versión admite adjuntos de hasta 2 MB. Usa CSV o un periodo menor."
        )
    try:
        app = msal.ConfidentialClientApplication(
            settings.GRAPH_CLIENT_ID,
            authority="https://login.microsoftonline.com/"
            + quote(settings.GRAPH_TENANT_ID, safe=""),
            client_credential=settings.GRAPH_CLIENT_SECRET,
        )
        token = app.acquire_token_for_client(
            scopes=["https://graph.microsoft.com/.default"]
        )
    except requests.RequestException as e:
        raise MailFailure("No se pudo obtener token Graph.", "retry") from e
    if "access_token" not in token:
        raise MailFailure(
            "Graph: autenticación denegada; revisa aplicación, secreto y consentimiento."
        )
    payload = {
        "message": {
            "subject": delivery.job.subject,
            "body": {"contentType": "Text", "content": delivery.job.body},
            "toRecipients": [{"emailAddress": {"address": delivery.recipient}}],
            "internetMessageHeaders": [
                {"name": "x-intranet-delivery", "value": str(delivery.pk)}
            ],
            "attachments": [
                {
                    "@odata.type": "#microsoft.graph.fileAttachment",
                    "name": path.name,
                    "contentBytes": base64.b64encode(path.read_bytes()).decode("ascii"),
                }
            ],
        },
        "saveToSentItems": True,
    }
    try:
        response = requests.post(
            "https://graph.microsoft.com/v1.0/users/"
            + quote(settings.GRAPH_SENDER, safe="")
            + "/sendMail",
            headers={"Authorization": "Bearer " + token["access_token"]},
            json=payload,
            timeout=(10, 60),
            allow_redirects=False,
        )
    except requests.RequestException as e:
        raise MailFailure("Graph: respuesta de envío desconocida.", "uncertain") from e
    if response.status_code == 202:
        return
    if response.status_code == 429:
        retry = response.headers.get("Retry-After", "300")
        raise MailFailure(
            "Graph: límite temporal de solicitudes.",
            "retry",
            delay=int(retry) if retry.isdigit() else 300,
        )
    if response.status_code >= 500 or response.status_code == 408:
        raise MailFailure(
            f"Graph: estado incierto ({response.status_code}).", "uncertain"
        )
    raise MailFailure(
        f"Graph rechazó el envío ({response.status_code}); revisa configuración/permisos."
    )


def send_delivery(delivery):
    msg, path = build_message(delivery)
    if settings.MAIL_PROVIDER == "file":
        settings.MAIL_FILE_PATH.mkdir(parents=True, exist_ok=True)
        (settings.MAIL_FILE_PATH / f"delivery-{delivery.pk}.eml").write_bytes(
            msg.message().as_bytes()
        )
        return "test"
    if settings.MAIL_PROVIDER == "smtp":
        smtp_send(msg)
    elif settings.MAIL_PROVIDER == "graph":
        graph_send(delivery, path)
    else:
        raise MailFailure("MAIL_PROVIDER debe ser file, smtp o graph.")
    return "accepted"
