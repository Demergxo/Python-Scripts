import cv2
import qrcode
import zxingcpp
from pathlib import Path

def limpiar_qr(ruta_imagen, salida="qr_limpio.png"):
    ruta = Path(ruta_imagen)
    if not ruta.exists():
        print(f"❌ No se encontró el archivo: {ruta_imagen}")
        return

    # Leer imagen
    img = cv2.imread(str(ruta))
    if img is None:
        print("❌ No se pudo leer la imagen.")
        return

    # Convertir a RGB (zxing-cpp trabaja mejor en ese formato)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Intentar decodificar con ZXing
    results = zxingcpp.read_barcode(img_rgb)

    if not results or not results.text:
        print("⚠️ No se detectó ningún QR en la imagen.")
        return

    data = results.text.strip()
    print(f"✅ QR detectado con contenido:\n{data}")

    # Regenerar QR limpio
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white")
    img_qr.save(salida)

    print(f"✅ QR limpio guardado como {salida}")

if __name__ == "__main__":
    #limpiar_qr(r"C:\Users\jgmeras\OneDrive - GXO\Documents\Python Scripts\Aplicaciones\Utilidades\20251029_151247.jpg")

    limpiar_qr(r"C:\Users\jgmeras\OneDrive - GXO\Documents\Python Scripts\Aplicaciones\Utilidades\20251029_152350.jpg")

