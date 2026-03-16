import os
import base64
import re

# Carpeta donde están los archivos de entrada
INPUT_FOLDER = r"C:\Users\jgmeras\OneDrive - GXO\Documents\01. Mahou\Try_edi"

# Carpeta donde se guardarán los EDI decodificados
OUTPUT_FOLDER = r"C:\Users\jgmeras\OneDrive - GXO\Documents\01. Mahou\Try_edi\edi_output"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def extract_base64(lines):
    """
    Encuentra dónde empieza el contenido base64.
    Primero busca 'Content-Disposition:'.
    Si no lo encuentra, empieza desde la línea 5.
    """
    start_index = None

    for i, line in enumerate(lines):
        if "Content-Disposition:" in line:
            start_index = i + 1
            break

    if start_index is None:
        start_index = 5

    base64_data = "".join(lines[start_index:]).strip()
    return base64_data


def decode_file(filepath):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    base64_data = extract_base64(lines)

    try:
        decoded = base64.b64decode(base64_data)
        return decoded
    except Exception as e:
        print(f"Error decodificando {filepath}: \n{e}")
        return None


def extract_segments(edi_text):
    """
    Busca los segmentos requeridos dentro del EDI
    """
    results = {}

    patterns = {
        "BGM+80E": r"BGM\+80E:([^']+)",
        "DTM+264": r"DTM\+264:([^']+)",
        "DTM+267": r"DTM\+267:([^']+)",
        "RFF+FCP": r"RFF\+FCP:([^']+)"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, edi_text)
        results[key] = match.group(1) if match else None

    return results


def process_files():

    for filename in os.listdir(INPUT_FOLDER):

        filepath = os.path.join(INPUT_FOLDER, filename)

        if not os.path.isfile(filepath):
            continue

        print(f"Procesando: {filename}")

        decoded = decode_file(filepath)

        if decoded is None:
            continue

        edi_text = decoded.decode("utf-8", errors="ignore")

        # Guardar EDI
        edi_name = os.path.splitext(filename)[0] + ".edi"
        edi_path = os.path.join(OUTPUT_FOLDER, edi_name)

        with open(edi_path, "w", encoding="utf-8") as f:
            f.write(edi_text)

        # Extraer segmentos
        segments = extract_segments(edi_text)

        print("Segmentos encontrados:")
        for k, v in segments.items():
            print(f"  {k}: {v}")

        print("-" * 40)


if __name__ == "__main__":
    process_files()