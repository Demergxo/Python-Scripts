# Proyecto actualizado: Windows 11 y correo programado

Empieza por `intranet_sql/LEEME_WINDOWS.md`.

La documentación histórica y los archivos de infraestructura del ZIP se conservan como referencia; no describen necesariamente esta versión. El código operativo está en intranet_sql.

La SQLite incluida es la instantánea original, sin modificar ni migrar. Si actualizas una instalación que ha seguido usándose, conserva su base vigente y haz copia antes de las migraciones.

El envío de correo y la conexión externa se entregan desactivados (`MAIL_PROVIDER=file`, `EXTERNAL_DB_ENABLED=false` en .env.example). Configurar el entorno siguiendo la guía.
