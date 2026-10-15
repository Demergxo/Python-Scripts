# Dashboard Mahou Steel

Integración de las dos conexiones de `PANEL MAHOU Steel v17.1.xlsx`, sin Datos Altia. Ruta: `/mahou/`. Versión: 5 de octubre de 2026.

## Qué incluye

- Consultas originales en `mahou/panel.sql` y `mahou/muelles.sql`, con saltos de línea normalizados. No se modifican sus cálculos, joins, NOLOCK, cliente 944, almacén 221 ni horizonte temporal.
- Consultas registradas como `MAHOU_PANEL` y `MAHOU_MUELLES`, categoría y grupo privados `Mahou`.
- Tabla principal con las 18 columnas XGA de PANEL C:T, en el mismo orden y agrupadas en GXO, preparación, total, pendiente, carga y seguimiento. Porcentajes 0–100, fechas y decimales formateados para lectura. Un NULL se muestra como raya, no como cero.
- Filtros Hoy/Ayer/Backlog/Mañana/Pasado mañana/Futuro, abierto/cerrado, estado XGA y búsqueda parcial por albarán, extracción, expediente, cliente y muelle. Valores iniciales Hoy y Abierto.
- Conteos de filas, albaranes distintos e incidencias 20-INC; distribución por estado. No se suman cantidades globales sin validar previamente la multiplicidad de los joins de la consulta.
- Muelles de carga: todas las coincidencias de las ubicaciones de la columna 31, incluyendo ubicaciones múltiples separadas por `|`. No utiliza el primer resultado de BUSCARV. Los números pertenecen a cada fila/pedido y no están desglosados por muelle.
- Ocupación DE y 88: Libre cuando NumPalets=0 y Ocupado cuando >0, con fecha de entrada más antigua. Es una consulta global del almacén 221 y no sigue los filtros de pedidos.
- CSV de todas las filas de la vista filtrada, no solo de la página de 100 filas. La pantalla formatea los datos; el CSV conserva valores de origen y protege texto que podría interpretarse como fórmula. Para XLSX completo se pueden usar las consultas registradas en el circuito habitual de ejecuciones.

## Exclusiones y diferencias deliberadas

No se importa la hoja Datos Altia, sus datos personales, fechas de booking/registro ni las alertas Crítico/Riesgo/En hora/Sin booking que dependen de ella. El orden de la tabla usa fecha XGA de carga y albarán; el Excel ordenaba por fecha Altia. Las hojas manuales Muelle Dedicado, CAPILAR 26.06 y Transferencias no tienen una consulta de conexión propia y no se convierten en información en vivo.

La hoja Muelles CA referencia BBDD!BC:BQ; la tabla BBDD del libro suministrado termina en AT. La integración utiliza el campo SQL de ubicaciones y todas sus coincidencias, sin reproducir esa dependencia de columnas vacías. No muestra como libre un muelle CA por no encontrar pedidos.

La consulta original incluye `FechaTeoricaCargaDoc >= DATEADD(DAY,-7,GETDATE())` sin fecha máxima. Backlog NO es el histórico completo. Los textos Hoy/Ayer se calculan en SQL Server al actualizar y permanecen congelados hasta la siguiente actualización. Las fechas XGA se presentan tal como las devuelve la conexión; hay que confirmar la zona horaria de SQL Server.

Se conserva NOLOCK para mantener la consulta original: la lectura puede observar cambios en curso. Las dos consultas se ejecutan consecutivamente y se publican juntas si ambas terminan; esto no es una transacción consistente de XGA ni garantiza una foto exacta del mismo instante. Se recomienda validar la consulta y el uso de NOLOCK con el responsable de base de datos.

## Instalación y actualización en Windows

1. Realizar copia coherente de la base SQLite y de la configuración, con los servicios detenidos. Conservar el paquete anterior para volver atrás.
2. Incorporar este código al proyecto conservando `.env`, `db.sqlite3` (o APP_DB_PATH), `var/` y la configuración local. NO sustituir una base de producción con la base incluida en el ZIP.
3. Desde PowerShell en la carpeta que contiene manage.py:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py install_mahou
.\.venv\Scripts\python.exe manage.py collectstatic --noinput
```

`install_mahou` no ejecuta consultas externas ni altera OUT01. Es repetible, conserva consultas existentes y sus permisos. `--update-sql` reemplaza expresamente el SQL y el alias de las dos consultas Mahou por los incluidos en el paquete. Una categoría Mahou existente sin grupos se rechaza para evitar publicar datos accidentalmente.

4. En el administrador, añadir los usuarios autorizados al grupo Mahou. El superusuario también puede acceder. Para ver la página, refrescar o descargar, se comprueba el acceso a AMBAS consultas activas, incluso al mostrar resultados ya guardados.
5. Crear o comprobar un DSN **de sistema de 64 bits** que apunte a la réplica indicada en el Excel y sea accesible por la cuenta Windows del servicio. El DSN del Excel se llama `conexion replicada`; no se copia su UID ni su nombre de equipo. La cuenta del servicio debe tener SELECT sobre los objetos utilizados.
6. Añadir o ajustar estas variables en `.env`:

```dotenv
MAHOU_DB_ENABLED=true
MAHOU_DSN=conexion replicada
MAHOU_DATABASE=XGA
MAHOU_DRIVER=ODBC Driver 18 for SQL Server
MAHOU_EXTRA_PARAMS=Trusted_Connection=yes;Encrypt=yes;TrustServerCertificate=no;ApplicationIntent=ReadOnly;
MAHOU_QUERY_TIMEOUT=300
MAHOU_AUTO_REFRESH_USER=
MAHOU_REFRESH_SECONDS=900
MAHOU_MAX_ROWS=20000
```

El DSN debe existir con ese nombre en el equipo de despliegue; también puede configurarse otro autorizado por IT. No se cambia XGA_DSN. El alias `mahou` es independiente del alias habitual `externa`. ApplicationIntent no sustituye los permisos de solo lectura. No desactivar la validación del certificado para resolver un error sin revisar el certificado/DSN con IT.

7. Reiniciar web, worker y scheduler después de migrar. No se requiere un servicio adicional ni una dependencia Python nueva. Los comandos existentes siguen siendo:

```powershell
.\.venv\Scripts\python.exe run_web.py
.\.venv\Scripts\python.exe manage.py run_reports worker
.\.venv\Scripts\python.exe manage.py run_reports scheduler
```

Si ya están instalados como servicios, reiniciarlos en lugar de ejecutar instancias duplicadas en consola. Los mismos roles y definiciones WinSW siguen vigentes. El proceso de correo no participa en la actualización del dashboard.

8. Abrir `/mahou/` con un usuario autorizado y pulsar Actualizar datos. El worker recoge la solicitud en segundo plano. Para refresco automático, configurar MAHOU_AUTO_REFRESH_USER con el **nombre de un usuario Django activo y autorizado**; no es la cuenta Windows. Reiniciar scheduler tras modificarlo. Vacío desactiva el refresco automático.

## Funcionamiento y carga

Una actualización lee ambas consultas y guarda la última pareja completa en la base de la aplicación. Abrir, filtrar, paginar y exportar el panel solo lee esa copia. No hay una consulta XGA por navegador. La pantalla revisa la copia cada 60 segundos (15 durante una actualización), sin interrumpir la edición de filtros ni un muelle desplegado. La actualización manual agrupa solicitudes concurrentes y aplica una espera mínima de un minuto; la automática usa 900 segundos por defecto, como el Excel.

El worker comparte la ejecución con los informes existentes y procesa una actualización Mahou y un informe en cada vuelta. Si OUT01 ya está ejecutándose, Mahou esperará a que termine. Esta versión no cancela trabajos en curso ni añade paralelismo contra XGA. Si se necesita una garantía de actualización independiente de OUT01, habrá que separar el consumidor y definir con IT la concurrencia permitida.

Si falla cualquiera de las dos consultas, se conserva la última copia completa y se muestra el fallo. Los detalles están en el registro del servicio y, para superusuarios, en Administración > Actualizaciones Mahou. Superar MAHOU_MAX_ROWS impide publicar datos parciales. Si el worker reinicia durante una actualización, la marca como fallida. La siguiente actualización automática o manual vuelve a solicitarla respetando el intervalo.

Una modificación del SQL, parámetros o alias invalida la visualización de la copia anterior hasta una nueva actualización. Revocar el acceso o desactivar una consulta bloquea también la descarga. Una nueva ejecución con las consultas genéricas usa igualmente el alias configurado.

No se envían emails desde el dashboard. Las dos consultas pueden programarse con el sistema habitual de informes, usando parámetros fijos vacíos `{}`. En ese caso se enviaría el resultado SQL, no una captura del dashboard.

## Verificaciones realizadas y pendientes

- 42 pruebas locales superadas, incluyendo 16 nuevas para Mahou y 26 existentes. Cobertura de permisos, revocación, CSRF, escape HTML/CSV, filtrado, publicación completa, conservación de datos tras fallo, cambios de consulta, límites, periodicidad y selección de conexión.
- Comparación independiente con los valores guardados del Excel: 607 filas BBDD; 131 filas con Hoy/Abierto. Los 18 campos XGA de esas 131 filas coinciden como conjunto con PANEL C:T, teniendo en cuenta que el Excel transforma algunos vacíos en cero. El orden por Altia queda excluido.
- La comprobación usa valores almacenados en el libro: no es una actualización contra XGA ni demuestra que los joins de origen no dupliquen datos.
- Pendiente en Windows: DSN, autenticación integrada, versión/capacidades de SQL Server para STRING_AGG, certificados, tiempos de las dos consultas, carga concurrente y validación de cantidades con Operaciones.
- Los datos del Excel se utilizaron solo en una base de prueba local. El paquete no precarga el dashboard con información histórica presentada como actual y no incluye el Excel adjunto.

## Pruebas reproducibles

```powershell
.\.venv\Scripts\python.exe manage.py test mahou core reports --settings=intranet_sql.test_settings
```

Estas pruebas desactivan las conexiones externas y el correo real. Los manuales Word anteriores describen la versión previa; este documento complementa sus pasos de despliegue para Mahou y el nuevo campo de conexión de las consultas.

La comprobación visual en un navegador real queda pendiente: el navegador automatizado no pudo instalarse en el entorno de desarrollo. Las respuestas HTML, sus estados y la exportación sí se han probado localmente.
