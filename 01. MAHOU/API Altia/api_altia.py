import getpass
import requests
import urllib3
from bs4 import BeautifulSoup


# Solo mientras resolvemos el certificado corporativo.
# Evita mostrar InsecureRequestWarning al usar verify=False.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #type:ignore


BASE_URL = "https://ictower.net"
LOGIN_URL = f"{BASE_URL}/Account/Login"
DATA_URL = f"{BASE_URL}/Mahou/Vision/Vision_ReadMultiple"

WAREHOUSE_ID = 60037

TIMEOUT = 30
VERIFY_SSL = False


def crear_sesion(email: str, password: str) -> requests.Session:
    """
    Abre el formulario de login, obtiene el token antifalsificación
    y autentica una sesión de requests.

    Las cookies quedan almacenadas únicamente en memoria dentro
    del objeto Session.
    """
    session = requests.Session()

    # Cabeceras generales de la sesión.
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/155.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    })

    try:
        # 1. Abrir la página de login.
        respuesta_login = session.get(
            LOGIN_URL,
            timeout=TIMEOUT,
            verify=VERIFY_SSL,
        )
        respuesta_login.raise_for_status()

        # 2. Analizar el formulario.
        soup = BeautifulSoup(respuesta_login.text, "html.parser")

        formulario = soup.find("form")

        if formulario is None:
            raise RuntimeError(
                "No se encontró el formulario de inicio de sesión."
            )

        # 3. Obtener el token antifalsificación.
        campo_token = formulario.find(
            "input",
            {"name": "__RequestVerificationToken"},
        )

        if campo_token is None or not campo_token.get("value"):
            raise RuntimeError(
                "No se encontró el token __RequestVerificationToken."
            )

        token = campo_token["value"]

        # 4. Determinar la URL real a la que envía el formulario.
        form_action = formulario.get("action")

        if form_action:
            post_url = requests.compat.urljoin( #type:ignore
                respuesta_login.url,
                form_action,
            )
        else:
            post_url = LOGIN_URL

        # 5. Payload adaptado a los name reales del formulario.
        payload = {
            "Email": email,
            "Password": password,
            "__RequestVerificationToken": token,
        }

        # Si el formulario tuviera RememberMe, se fuerza a false.
        if formulario.find("input", {"name": "RememberMe"}):
            payload["RememberMe"] = "false"

        # 6. Enviar el login sin seguir la redirección.
        respuesta_post = session.post(
            post_url,
            data=payload,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": respuesta_login.url,
            },
            timeout=TIMEOUT,
            verify=VERIFY_SSL,
            allow_redirects=False,
        )

        print(f"Login HTTP: {respuesta_post.status_code}")
        print(
            "Redirección del login:",
            respuesta_post.headers.get("Location"),
        )

        # Habitualmente, un login ASP.NET correcto devuelve una
        # redirección 302. También contemplamos otros códigos 3xx.
        if respuesta_post.status_code not in (200, 301, 302, 303):
            raise RuntimeError(
                "El servidor rechazó la petición de login. "
                f"HTTP {respuesta_post.status_code}"
            )

        # 7. Verificar que la sesión contiene la cookie de autenticación.
        nombres_cookies = {
            cookie.name
            for cookie in session.cookies
        }

        if ".AspNet.ApplicationCookie" not in nombres_cookies:
            # No mostramos los valores de las cookies.
            raise RuntimeError(
                "No se generó .AspNet.ApplicationCookie. "
                "Las credenciales pueden ser incorrectas o el formulario "
                "puede requerir algún campo adicional."
            )

        print("Autenticación correcta.")
        print("Cookie ASP.NET generada en memoria.")

        return session

    except Exception:
        session.cookies.clear()
        session.close()
        raise


def consultar_movimientos(
    session: requests.Session,
    warehouse_id: int = WAREHOUSE_ID,
    matricula_camion: str = "",
    matricula_remolque: str = "",
    codigo: str = "",
    conductor: str = "",
    telefono: str = "",
    mostrar_finalizados: bool = False,
    tipo_actividad: str = "",
) -> list:
    """
    Consulta el endpoint utilizado por la pantalla Vision.
    """

    params = {
        "warehouseId": warehouse_id,
        "truckPlate": matricula_camion,
        "trailerPlate": matricula_remolque,
        "code": codigo,
        "driver": conductor,
        "phone": telefono,
        "showLoaded": str(mostrar_finalizados).lower(),
        "activityType": tipo_actividad,
    }

    respuesta = session.get(
        DATA_URL,
        params=params,
        headers={
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{BASE_URL}/Mahou/Vision",
        },
        timeout=TIMEOUT,
        verify=VERIFY_SSL,
        allow_redirects=False,
    )

    # Si responde con redirección al login, la sesión no es válida
    # o ya ha caducado.
    if respuesta.status_code in (301, 302, 303):
        destino = respuesta.headers.get("Location", "")

        if "/Account/Login" in destino:
            raise RuntimeError(
                "La sesión no ha sido aceptada o ha caducado. "
                f"Redirección recibida: {destino}"
            )

        raise RuntimeError(
            f"Redirección inesperada: {destino}"
        )

    respuesta.raise_for_status()

    content_type = respuesta.headers.get("Content-Type", "")

    if "application/json" not in content_type.lower():
        inicio_respuesta = respuesta.text[:200].replace("\n", " ")

        raise RuntimeError(
            "ICTower no devolvió JSON. "
            f"Content-Type: {content_type}. "
            f"Inicio de la respuesta: {inicio_respuesta}"
        )

    datos = respuesta.json()

    if not isinstance(datos, list):
        raise RuntimeError(
            "La respuesta JSON no contiene la lista esperada."
        )

    return datos


def mostrar_movimientos(movimientos: list[dict]) -> None:
    print(f"\nMovimientos recibidos: {len(movimientos)}\n")

    for movimiento in movimientos:
        codigo = movimiento.get("Code", "")
        tipo = movimiento.get("TypeText", "")
        estado = movimiento.get("State", "")
        hora = movimiento.get("DateStart", "")
        muelle = movimiento.get("Dock") or "-"
        destino = (movimiento.get("Destination") or "").strip()

        print(
            f"{codigo:<8} | "
            f"{tipo:<8} | "
            f"{estado:<12} | "
            f"{hora:<5} | "
            f"Muelle: {muelle:<4} | "
            f"{destino}"
        )


def main() -> None:
    # El usuario se escribe normalmente.
    email = input("Usuario / correo de ICTower: ").strip()

    # La contraseña no se muestra por pantalla.
    password = getpass.getpass("Contraseña de ICTower: ")

    session = None

    try:
        session = crear_sesion(
            email=email,
            password=password,
        )

        movimientos = consultar_movimientos(
            session=session,
            warehouse_id=60037,
            mostrar_finalizados=False,
        )

        mostrar_movimientos(movimientos)

    except requests.RequestException as error:
        print(f"\nError de conexión: {error}")

    except RuntimeError as error:
        print(f"\nError: {error}")

    except ValueError as error:
        print(f"\nError procesando el JSON: {error}")

    finally:
        # La contraseña solo queda referenciada durante esta ejecución.
        password = None

        if session is not None:
            # Elimina todas las cookies almacenadas en memoria.
            session.cookies.clear()

            # Cierra las conexiones HTTP.
            session.close()

            print("\nSesión local cerrada y cookies eliminadas de memoria.")


if __name__ == "__main__":
    main()