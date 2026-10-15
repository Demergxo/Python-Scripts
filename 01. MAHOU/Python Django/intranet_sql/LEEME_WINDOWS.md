# Actualización Mahou

Para incorporar el panel del Excel y su conexión independiente, sigue **MAHOU_DESPLIEGUE.md** después de los pasos base de este documento. No reemplaces tu base de producción con la del paquete.

# Intranet SQL — Windows 11, programaciones y correo

Versión preparada el 03/10/2026. Empieza por este documento; la documentación histórica del ZIP describe la versión anterior.

## Qué cambia

- Las consultas interactivas pasan a una cola persistente. El navegador no mantiene una petición SQL abierta.
- Una ejecución genera CSV y Excel completos, por lotes de 2.000 filas, con una vista previa de 300 filas. Descargar no ejecuta de nuevo SQL.
- Nuevo administrador: **Programaciones**, **Ejecuciones**, **Envíos**. Menú web: **Mis ejecuciones**.
- Fechas puntuales, cada N horas, días, semanas y meses; periodos fijos, hoy, ayer, semana anterior y mes anterior.
- SMTP y Microsoft Graph seleccionables por configuración. Se entrega con `MAIL_PROVIDER=file`: genera .eml locales, no envía.
- Un envío por destinatario: no expone la lista al resto y permite registrar fallos individualmente.
- Reintentos solo para rechazos temporales conocidos. Un envío incierto requiere revisión manual. Reenviar usa el archivo existente.
- Corregidos los permisos de exportación, la validación de fechas con mayúsculas y el día adicional en Pal_in_out.
- Configuración fuera del código; secreto nuevo al instalar; sesiones en base de datos.

No se ha ejecutado nada contra XGA ni enviado correo real. OUT01 activa no se ha cambiado. En `sql/` se incluye una candidata para comparación. Esta versión mejora la gestión del tiempo de espera y evita repetir consultas: no promete acelerar el SQL activo.

## Componentes

| Proceso | Función | Comando |
|---|---|---|
| web | Django / Waitress | `python run_web.py` |
| scheduler | Examina cada 10 s horarios persistidos y crea trabajos | `python manage.py run_reports scheduler` |
| worker | Ejecuta un informe cada vez y genera sus dos archivos | `python manage.py run_reports worker` |
| mail | Envía los archivos terminados; no se bloquea detrás de OUT01 | `python manage.py run_reports mail` |

Usar el mismo proyecto, `.env`, base SQLite y REPORT_ROOT para los cuatro. Un solo equipo, un proceso por rol. Cada proceso de fondo obtiene un bloqueo de archivo del sistema operativo para impedir instancias duplicadas. No trasladar SQLite o los bloqueos a una unidad de red ni desplegar varios equipos con esta implementación.

La base original incluida se conserva byte a byte, sin migrar y sin tareas nuevas. Conserva tus usuarios, consultas y registros del momento del ZIP. **Al actualizar una instalación existente, conserva su base vigente; no copies encima la instantánea de este paquete.**

## 1. Preparación local

Instalar Python 3.12 x64. Copiar `intranet_sql` a `C:\IntranetSQL\intranet_sql` (las plantillas de despliegue usan esa ruta; se puede cambiar).

En PowerShell, desde ese directorio:

```powershell
.\deploy\setup.ps1
```

El script crea `.venv`, instala las versiones fijadas en `requirements.txt` y crea `.env` con una clave aleatoria solo si no existe. No migra ni arranca servicios. Si la política de PowerShell impide scripts, usar el procedimiento aprobado por IT; también se pueden ejecutar manualmente sus comandos. No se necesita debilitar permanentemente la política.

Editar `.env`. Inicialmente mantener:

```ini
EXTERNAL_DB_ENABLED=false
MAIL_PROVIDER=file
HTTPS_ENABLED=false
TRUST_PROXY_HEADERS=false
```

La configuración antigua `local_settings.py` ya no se importa. Todas las opciones operativas están en `.env` o variables de entorno (estas últimas tienen prioridad). No guardar `.env` en repositorios ni compartirlo junto al ZIP. Protegerlo con permisos NTFS para administradores y cuentas de servicio.

Parar la versión anterior y hacer una copia de la base vigente y su configuración antes de continuar. Si SQLite está usando WAL, realizar una copia coherente con SQLite backup o tras cerrar todas sus conexiones; no copiar solo db.sqlite3 mientras se está escribiendo.

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py collectstatic --noinput
.\.venv\Scripts\python.exe manage.py check
```

En una base vacía, crear un administrador con `manage.py createsuperuser`. Con la base incluida ya existen los usuarios originales. Cambiar el secreto y el backend de sesiones obliga a volver a iniciar sesión.

Para probar interfaz local sin IIS/Caddy, establecer temporalmente `DJANGO_DEBUG=true` y ejecutar `manage.py runserver 127.0.0.1:8000`. Solo para prueba local; sirve también los estáticos del administrador. Volver a false antes de servicio. Waitress solo sirve Django: los estáticos de producción los sirve IIS o Caddy.

## 2. Acceso de solo lectura a XGA

La identidad SQL es **la cuenta Windows del proceso worker**. Las programaciones tienen, además, un responsable Django para permisos y auditoría. Ese usuario Django no se convierte en una cuenta Windows ni se suplanta.

Hoy puedes probar el worker en una consola abierta con tu sesión. Al pasar a la cuenta definitiva, IT debe configurar en Windows:

- Derecho de inicio de sesión como servicio para esa cuenta.
- Acceso de lectura a XGA mediante autenticación integrada.
- DSN **de sistema**, x64, `XGA_PROD` visible para esa cuenta; no depender del DSN de usuario de tu sesión.
- Acceso NTFS a la base, carpeta de resultados y logs.

Revisar el driver instalado. Se propone ODBC Driver 18; si se conserva otro, el DSN debe apuntar al correcto y `XGA_DRIVER` reflejarlo. La validación de certificado depende del driver/DSN/servidor: usar certificado de confianza según IT, no desactivar la validación como solución automática.

Activar `EXTERNAL_DB_ENABLED=true` después. `XGA_QUERY_TIMEOUT=1800` limita una sentencia a 30 minutos; no es un límite global del archivo ni una cancelación garantizada de todo trabajo remoto. OUT01 de tres meses excedió ese tiempo históricamente: probar periodos pequeños y optimizar antes de aumentar el límite.

Se mantiene la defensa SELECT/WITH y se rechaza SELECT INTO. El filtro por palabras no es una frontera de seguridad completa: mantener siempre la cuenta externa en solo lectura y restringir quién puede editar consultas.

## 3. Servicios Windows

Se incluyen plantillas para WinSW 2.x. IT debe aprobar y obtener el binario desde su distribución oficial. No se incluye ni descarga automáticamente.

```powershell
.\deploy\make-services.ps1 -WinSW C:\Herramientas\WinSW-x64.exe
```

Genera cuatro EXE/XML bajo `services`. No instala ni inicia nada. En consola elevada, registrar cada uno:

```powershell
.\services\intranet-web.exe install
.\services\intranet-scheduler.exe install
.\services\intranet-worker.exe install
.\services\intranet-mail.exe install
```

**Antes de iniciarlos**, abrir `services.msc` y configurar la cuenta prevista en Iniciar sesión. No dejar el worker ejecutándose como LocalSystem suponiendo que usará tu usuario. Se puede usar la cuenta única definitiva para los cuatro; el permiso de XGA solo lo necesita worker.

Iniciar con `start` sobre cada EXE o desde Servicios. Las plantillas configuran inicio automático, recuperación y rotación de logs. Para parar: `stop`. Para retirar: `stop`, luego `uninstall`.

Configurar que el equipo no se suspenda durante las ventanas de servicio. Los apagados/reinicios interrumpen trabajos; al reiniciar:

- SQL que estaba ejecutándose queda **Interrumpido**, sin reintento automático. Puede solicitarse otra ejecución tras revisar.
- Correo que estaba enviándose queda **Incierto**, sin reenvío automático.
- El planificador procesa como máximo una ocurrencia atrasada por programación, dentro de la tolerancia. El resto no se reproduce en ráfaga.
- Si se supera la tolerancia, registra una ocurrencia **Omitida** y calcula el siguiente horario.

## 4A. Publicación con IIS

Requiere edición de Windows con IIS y aprobación de IT para ARR/URL Rewrite.

1. Crear un sitio IIS con un directorio físico **separado y vacío**, nunca el directorio del proyecto (contiene base y configuración).
2. Configurar nombre DNS, enlace HTTPS y certificado corporativo. Restringir los bindings al nombre previsto.
3. Habilitar proxy en ARR y preservar la cabecera Host (`preserveHostHeader`).
4. Autorizar `HTTP_X_FORWARDED_PROTO` en las variables permitidas de URL Rewrite. El proxy debe establecerla, nunca confiar en el valor enviado por el cliente.
5. Copiar `deploy/web.config.example` como web.config al directorio del sitio.
6. Crear directorio virtual `/static` apuntando a `C:\IntranetSQL\intranet_sql\staticfiles`, con lectura. No publicar `var`, `.env`, SQLite ni el código.
7. En `.env`, configurar `DJANGO_ALLOWED_HOSTS=intranet.empresa.local,localhost,127.0.0.1`, `DJANGO_CSRF_TRUSTED_ORIGINS=https://intranet.empresa.local`, `HTTPS_ENABLED=true` y `TRUST_PROXY_HEADERS=true`.
8. Reiniciar web y comprobar login, administrador y una descarga. Waitress permanece en 127.0.0.1:8000, sin exposición directa.

La configuración concreta de ARR, certificados, binding y firewall debe comprobarse en ese Windows; aquí no se ha podido ejecutar IIS.

## 4B. Alternativa Caddy

Caddy sustituye solo a IIS. Usar `deploy/Caddyfile.example`, adaptando dominio y rutas del certificado/clave. La clave privada debe estar protegida; el certificado corporativo debe ser de confianza en los clientes.

Mantener las mismas variables HTTPS/hosts del caso IIS. Instalar Caddy como servicio siguiendo su documentación. Publicar únicamente HTTPS y `/static`; los archivos de informes se descargan a través de Django con comprobación de permisos.

Si tampoco autorizan Caddy, pedir un proxy corporativo existente. La aplicación y las colas no necesitan rehacerse. Waitress directo queda para pruebas locales, no se propone exponer credenciales de usuarios por HTTP en la red.

## 5. Configuración de correo

La identidad remitente de correo es independiente de la cuenta Windows/SQL. Cambiar `MAIL_PROVIDER` y reiniciar **mail** permite cambiar de proveedor sin editar horarios o SQL. No cambiar de proveedor automáticamente ante un error: podría duplicar correos o usar una identidad no prevista.

### SMTP

```ini
MAIL_PROVIDER=smtp
MAIL_FROM=informes@empresa.example
SMTP_HOST=relay.empresa.example
SMTP_PORT=25
SMTP_TLS=false
SMTP_SSL=false
SMTP_USER=
SMTP_PASSWORD=
```

Valores ilustrativos: usar los proporcionados por IT. Algunos relays autorizan la IP o el remitente sin usuario/clave; otros exigen TLS y credenciales. Este adaptador admite relay sin autenticación o login SMTP con TLS/SSL. No implementa NTLM/Kerberos ni OAuth de SMTP; para autenticación moderna usar Graph.

### Microsoft Graph

```ini
MAIL_PROVIDER=graph
GRAPH_TENANT_ID=...
GRAPH_CLIENT_ID=...
GRAPH_CLIENT_SECRET=...
GRAPH_SENDER=informes@empresa.example
MAIL_FROM=informes@empresa.example
```

Aplicación de Entra con permisos de aplicación `Mail.Send`, consentimiento administrativo y acceso limitado por IT al buzón remitente. No precisa abrir Outlook ni iniciar una sesión interactiva. Guardar el secreto fuera del código y gestionar su caducidad. Esta implementación usa secreto de cliente; certificados de aplicación requerirían ampliar el adaptador.

**Adjuntos:** límite predeterminado de 2.000.000 bytes por archivo. SMTP puede ajustarse al límite del relay; Graph mantiene un máximo de 2 MB en este adaptador para usar sendMail directo con margen. No se implementan sesiones de carga para adjuntos grandes ni enlace automático en lugar del adjunto. Si se excede, el informe queda disponible en la web y el envío aparece Fallido. CSV o un periodo menor pueden resolverlo.

Cada destinatario tiene un registro independiente. No se incluyen las direcciones del resto en el mensaje. Aceptado por servidor no confirma entrega final ni ausencia de rebotes. Los rechazos transitorios conocidos tienen hasta tres intentos; los errores inciertos no se reintentan.

Para cambiar de pruebas a real: los envíos en estado **Guardado de prueba** no se envían solos. Seleccionarlos en Envíos y usar la acción explícita de reenvío, o crear una nueva ejecución. Esto evita enviar de golpe un historial de pruebas.

## 6. Uso de programaciones

Abrir `/admin/reports/schedule/`. Las nuevas tareas están inactivas por defecto. Superusuarios pueden administrarlo todo. Otros usuarios necesitan `is_staff`, permisos Django de reports y acceso a la categoría; solo ven sus propias programaciones/ejecuciones en ese administrador.

Ejemplo mensual: OUT01, mensual, día 1, 06:00, periodo mes anterior, Excel, destinatarios uno por línea. Las variables de asunto/cuerpo son `{query}`, `{start}`, `{end}`, `{job_id}`. No se ejecuta código ni se evalúan plantillas arbitrarias.

Los parámetros JSON permiten completar valores adicionales de cada consulta. Si el periodo es relativo, reemplaza las fechas con los nombres exactos definidos en QueryParam, reconociendo fecha_inicio/fecha_fin sin distinguir mayúsculas. El periodo se resuelve según el instante programado en Madrid, no el momento en que termina el trabajo.

Para intervalos por horas, indicar el inicio en “Fecha puntual / inicio del intervalo”. Semanal acepta `mon-fri` o `mon,wed,fri`. Mensual acepta 1..31 o `last`; día 31 omite meses sin ese día. Los horarios se calculan con los triggers de APScheduler 3.x. Cerca del cambio de hora, una hora local puede faltar o repetirse; evitar 02:00–02:59 en programaciones diarias críticas. Los intervalos representan horas transcurridas, no una hora fija de reloj.

Guardar una programación activa recalcula su próxima ejecución futura. Pausar no cancela trabajos ya encolados ni envíos ya creados. “Ejecutar ahora” toma los datos actuales de la tarea y encola también el correo. Evita solapamiento con otro trabajo de esa misma programación.

No hay porcentaje de progreso de SQL: se muestran estados. No hay botón de cancelar una sentencia ya ejecutándose. Los errores se ven en administrador y logs; aún no hay avisos automáticos de fallo por correo.

Los resultados quedan asociados al usuario solicitante. El permiso de categoría se comprueba al crear, ejecutar y descargar; también antes de enviar. Para compartir un resultado web entre usuarios haría falta añadir un permiso explícito (no se publica por URL pública).

## 7. Operación, conservación y límites

SQLite permanece como almacenamiento local de aplicación; transacciones cortas con IMMEDIATE y espera de 30 s. No mantiene una transacción SQLite abierta durante SQL externo ni mientras envía. No se ha probado una carga multiusuario grande. Para varias máquinas/ejecutores o un volumen sostenido de escrituras, migrar la base y sustituir el bloqueo local por coordinación compartida.

REPORT_MAX_ROWS tiene valor inicial de un millón (por debajo del límite de hoja Excel). Si se excede o falla la generación, la ejecución no publica un resultado parcial. CSV usa UTF-8 BOM, separador punto y coma y neutraliza fórmulas en texto; Excel conserva las cadenas como texto. La vista previa convierte valores a texto, los archivos mantienen números.

Se generan ambos formatos por ejecución, aunque el correo adjunte solo uno. No existe caché histórica por día ni consolidación automática: eso requiere validar cómo se corrigen datos históricos de XGA. No se reutilizan resultados viejos silenciosamente al pedir una ejecución nueva.

Los archivos, registros y correos .eml de prueba se conservan sin borrado automático en esta versión. Acordar retención y vigilar espacio antes de uso continuado. Guardar copias coherentes de la base y de REPORT_ROOT. Si IT mueve datos, todos los servicios deben utilizar las mismas rutas y permisos. La carpeta no debe estar publicada por IIS/Caddy.

Cada cambio en SQL o definición de parámetros invalida un trabajo pendiente de esa consulta: se marca Fallido y hay que crearlo de nuevo. Se guardan parámetros, huella del SQL/esquema, estado y tiempos. No se pretende una auditoría inmutable del contenido SQL ni de todas las transiciones de envío.

## 8. Verificación y puesta en marcha

```powershell
.\.venv\Scripts\python.exe manage.py test reports --settings=intranet_sql.test_settings
.\.venv\Scripts\python.exe manage.py check --deploy
```

Las pruebas usan SQL/correo simulados y una base temporal, no XGA. Se han comprobado localmente formularios, permisos, exportación de 501 filas, descarga sin repetir SQL, planificación, solapamientos, fechas, SQL modificado, correo de prueba y respuestas simuladas SMTP/Graph. También se han aplicado las migraciones a una copia de la SQLite original.

Antes de producción validar en Windows: driver/DSN/cuenta de servicio, un informe corto real y sus cifras, un envío real a un destinatario de prueba autorizado, HTTPS/estáticos, tamaño de adjuntos, reinicio y recuperación. Resolver las advertencias relevantes de check --deploy según la política HTTPS de IT; HSTS no se activa automáticamente antes de validar certificados.

Rollback: parar los cuatro servicios, restaurar la copia de código/configuración/base anterior y su forma de arranque. No basta con volver al código viejo dejando una base y sesiones de la nueva versión sin evaluar la compatibilidad.

## Referencias

- Waitress: https://docs.pylonsproject.org/projects/waitress/en/latest/
- APScheduler 3.x: https://apscheduler.readthedocs.io/en/3.x/userguide.html
- Microsoft Graph sendMail: https://learn.microsoft.com/en-us/graph/api/user-sendmail
- mssql-django: https://github.com/microsoft/mssql-django
- IIS proxy: https://learn.microsoft.com/en-us/iis/extensions/url-rewrite-module/reverse-proxy-with-url-rewrite-v2-and-application-request-routing
- Caddy Windows: https://caddyserver.com/docs/running
- WinSW: https://github.com/winsw/winsw
