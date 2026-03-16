import base64
import io
from PIL import Image, ImageDraw, ImageFont
from pylibdmtx.pylibdmtx import encode, decode
import easygui as eg
import os


# Conversión de centímetros a píxeles a 300 DPI
def cm_to_px(cm, dpi=300):
    return int((cm / 2.54) * dpi)

# Genera los códigos según la casuística
def generar_codigos():
    codigos = []

    # 1. AF, CO, FN, R1, R2, RE y RT → 01 a 15
    for prefijo in ["AF", "CO", "FN", "R1", "R2", "RE", "RT"]:
        for i in range(1, 16):
            codigos.append(f"{prefijo}00000{i:02}")

    # 2. DE → 01 a 17
    for i in range(1, 18):
        codigos.append(f"DE00000{i:02}")

    # 3. CA → 01 a 43
    for i in range(1, 44):
        codigos.append(f"CA00000{i:02}")

    # 4. MA → esquema complejo
    esquema_MA = {
        1: (99, ['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6']),
        2: (99, ['C0', 'C1', 'C2', 'C3', 'C4']),
        3: (99, ['C0', 'C1', 'C2', 'C3', 'C4']),
        4: (99, ['C0', 'C1', 'C2', 'C3', 'C4']),
        5: (99, ['C0', 'C1', 'C2', 'C3', 'C4']),
        6: (96, []),
        7: (96, []),
        8: (96, []),
        9: (96, []),
        10: (99, ['C0', 'C1', 'C2']),
    }
    fijo = '000'

    for bloque, (num_normales, extras) in esquema_MA.items():
        for i in range(1, num_normales + 1):
            codigos.append(f"MA{bloque:02}{fijo}{i:02}")
        for extra in extras:
            codigos.append(f"MA{bloque:02}{fijo}{extra}")

    # 5. PI → esquema complejo
    esquema_PI = {
        1: (99, ['C0']),
        2: (99, ['C0']),
        3: (99, ['C0']),
        4: (99, ['C0', 'D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9']),
        5: (99, ['C0', 'D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9']),
        6: (99, ['C0', 'D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9']),
    }

    for bloque, (num_normales, extras) in esquema_PI.items():
        for i in range(1, num_normales + 1):
            codigos.append(f"PI{bloque:02}{fijo}{i:02}")
        for extra in extras:
            codigos.append(f"PI{bloque:02}{fijo}{extra}")

    return codigos


# Función auxiliar para cargar imágenes desde base64
def image_from_base64(image_base64, width, height):
    if not image_base64:
        return None
    try:
        im_bytes = base64.b64decode(image_base64)
        im = Image.open(io.BytesIO(im_bytes)).convert("RGBA")
        im = im.resize((width, height), Image.LANCZOS)
        return im
    except Exception as e:
        print(f"Error cargando imagen base64: {e}")
        return None

# Generar DataMatrix con segno
def generar_datamatrix(codigo):
    try:
        # encode devuelve un objeto Encoded
        encoded = encode(codigo.encode("utf-8"))

        # Creamos la imagen a partir de los píxeles
        dm_image = Image.frombytes(
            "RGB",                      # modo de color
            (encoded.width, encoded.height),
            encoded.pixels
        ).convert("RGBA")              # si quieres trabajar en RGBA

        return dm_image
    except Exception as e:
        print(f"Error generando DataMatrix para {codigo}: {e}")
        return None

#Para generar subdirectorios según necesidades
def obtener_directorio_para_codigo(codigo, directorio_base):
    prefijo = codigo[:2]  # AF, CO, DE, MA, PI, etc.

    # Por defecto: <base>/<prefijo>
    directorio = os.path.join(directorio_base, prefijo)

    # Para MA y PI, además, subcarpetas por bloque: MA01, MA02, PI04, etc.
    if prefijo in ("MA", "PI") and len(codigo) >= 4:
        bloque = codigo[2:4]  # "01", "02", "04", etc.
        directorio = os.path.join(directorio_base, prefijo, bloque)

    os.makedirs(directorio, exist_ok=True)
    return directorio


# Función principal
def generar_imagen(codigo, directorio_base, image_base64_sup=None, image_base64_inf=None):
    # Elegir carpeta según código (prefijo y, si aplica, bloque)
    directorio = obtener_directorio_para_codigo(codigo, directorio_base)

    # Generar DataMatrix
    datamatrix = generar_datamatrix(codigo)
    if datamatrix is None:
        raise RuntimeError(f"No se pudo generar DataMatrix para el código {codigo}")

    # Tamaño A4 horizontal a 300 DPI
    a4_width = cm_to_px(29.7)
    a4_height = cm_to_px(21)
    img = Image.new("RGBA", (a4_width, a4_height), "white")
    draw = ImageDraw.Draw(img)

    # Zonas reservadas (10 x 5 cm)
    zona_w = cm_to_px(10)
    zona_h = cm_to_px(5)

    zona_izq_sup = (0, 0)
    zona_der_inf = (a4_width - zona_w, a4_height - zona_h)

    # Cargar y pegar imágenes base64 (si vienen)
    im_sup = image_from_base64(image_base64_sup, zona_w, zona_h)
    if im_sup:
        img.paste(im_sup, zona_izq_sup, im_sup)

    im_inf = image_from_base64(image_base64_inf, zona_w, zona_h)
    if im_inf:
        img.paste(im_inf, zona_der_inf, im_inf)

    # Escalar DataMatrix a 10x10 cm
    dm_target = cm_to_px(10)  # ~1181 px a 300 DPI
    datamatrix = datamatrix.resize((dm_target, dm_target), Image.NEAREST)
    dm_w, dm_h = datamatrix.size

    # Centrar el DataMatrix
    dm_x = (a4_width - dm_w) // 2
    dm_y = (a4_height - dm_h) // 2 - cm_to_px(1.5)
    if dm_y < zona_h + cm_to_px(0.5):
        dm_y = zona_h + cm_to_px(0.5)

    img.paste(datamatrix, (dm_x, dm_y), datamatrix)

    # Añadir texto debajo del DataMatrix
    try:
        font = ImageFont.truetype("arial.ttf", 160)
    except:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), codigo, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_x = (a4_width - text_w) // 2
    text_y = dm_y + dm_h + cm_to_px(0.8)
    if text_y + text_h > a4_height - zona_h - cm_to_px(0.5):
        text_y = a4_height - zona_h - text_h - cm_to_px(0.5)

    draw.text((text_x, text_y), codigo, fill="black", font=font)

    # Guardar resultado en la carpeta correspondiente
    filename = os.path.join(directorio, f"{codigo}.png")
    img.convert("RGB").save(filename, "PNG")
    return filename




def generate_all():
    # Pedir nombre del directorio (igual que querías antes)
    directoy_name = eg.enterbox(
        msg="Nombre del Directorio donde se va a guardar (se creará dentro del directorio actual):",
        title="Control",
        default="",
        strip=True
    )

    if not directoy_name:
        eg.msgbox("No se indicó nombre de directorio. Saliendo.", "Aviso")
        return

    directory = os.path.join(os.getcwd(), directoy_name)
    os.makedirs(directory, exist_ok=True)

    image_base64_sup = "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" #imagen superior
    image_base64_inf = "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" #imagen inferior

    codigos = generar_codigos()
    total = len(codigos)
    rcnt = 0
    eg.msgbox(f"Se van a generar {total} imágenes A4 en:\n{directory}", "Inicio")

    for i, codigo in enumerate(codigos, start=1):
        try:
            ruta = generar_imagen(
                codigo,
                directory,  # directorio base
                image_base64_sup=image_base64_sup,
                image_base64_inf=image_base64_inf
            )
            rcnt += 1
            print(f"{i}/{total} - {codigo} -> {ruta}")
        except Exception as e:
            print(f"ERROR al generar {codigo}: {e}")


    eg.msgbox(f"Proceso finalizado. {rcnt}/{total} imágenes generadas en:\n{directory}", "Finalizado")
    print("Finalizado.")

if __name__ == "__main__":
    generate_all()
