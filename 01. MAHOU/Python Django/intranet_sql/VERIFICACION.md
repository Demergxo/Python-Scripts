# Verificación local — 03/10/2026

- 26 pruebas automatizadas superadas con Python 3.12 y Django 5.2.17.
- Formularios y páginas renderizados mediante cliente de pruebas Django.
- CSV y XLSX de 501 filas completos, vista previa de 300 y una única invocación de SQL simulada.
- Fechas de fin, periodos relativos, último día de mes, intervalo, hora de Madrid, omisión por retraso y solapamientos.
- Permisos en descarga/exportación, revocación antes de ejecución e invalidación por cambios de SQL.
- Circuito programación -> resultado -> dos correos de prueba .eml.
- Respuestas SMTP y Graph simuladas; no se hicieron envíos reales.
- Reintentos temporales limitados e interrupciones de envío sin repetición automática.
- Migración aplicada satisfactoriamente a una copia de la base incluida.
- La base incluida permanece idéntica byte a byte al original.
- Las nueve consultas existentes y la candidata OUT01 pasan el filtro SELECT/WITH.
- Django check sin incidencias y makemigrations --check sin cambios pendientes.

Pendientes en entorno corporativo: Windows 11/servicios/PowerShell, IIS o Caddy, certificados, DSN y driver, SQL real y equivalencia/rendimiento de OUT01, correo SMTP/Graph real. Las pruebas no acreditan esos puntos ni un rendimiento bajo carga.
