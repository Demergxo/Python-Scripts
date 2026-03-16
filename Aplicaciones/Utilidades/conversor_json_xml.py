import xml.etree.ElementTree as ET
import json

def json_a_xml_oracle(archivo_json, archivo_xml):
    try:
        with open(archivo_json, 'r', encoding='utf-8') as f:
            datos_json = json.load(f)

        def construir_elemento(diccionario, nombre):
            """ Construye un elemento XML recursivamente. """
            elemento = ET.Element(nombre.upper())  # Convertir etiquetas a mayúsculas

            if isinstance(diccionario, dict):
                for clave, valor in diccionario.items():
                    subelemento = ET.SubElement(elemento, clave.upper())
                    if isinstance(valor, dict):
                        subelemento.extend(construir_elemento(valor, clave))
                    elif isinstance(valor, list):
                        for item in valor:
                            item_elemento = ET.SubElement(subelemento, clave.upper())  # Sub-elemento de lista
                            item_elemento.extend(construir_elemento(item, clave) if isinstance(item, dict) else [])
                            item_elemento.text = str(item) if not isinstance(item, dict) else None
                    else:
                        subelemento.text = str(valor)
            elif isinstance(diccionario, list):  # Manejo de listas en la raíz
                for item in diccionario:
                    item_elemento = ET.Element(nombre.upper()) 
                    item_elemento.extend(construir_elemento(item, nombre) if isinstance(item, dict) else [])
                    item_elemento.text = str(item) if not isinstance(item, dict) else None
                    elemento.append(item_elemento)
            else:
                elemento.text = str(diccionario)

            return [elemento]

        root_nombre = list(datos_json.keys())[0]
        root_elemento = construir_elemento(datos_json[root_nombre], root_nombre)[0]

        tree = ET.ElementTree(root_elemento)
        tree.write(archivo_xml, encoding='utf-8', xml_declaration=True)

        print(f'Conversión completada: {archivo_xml}')
    except Exception as e:
        print(f'Error durante la conversión: {e}')

if __name__ == "__main__":
    archivo_json = r"C:\Users\jgmeras\Downloads\conexiones.json"  # Reemplaza con la ruta de tu archivo JSON
    archivo_xml = r"C:\Users\jgmeras\Downloads\salida.xml"  # Reemplaza con la ruta de salida XML
    json_a_xml_oracle(archivo_json, archivo_xml)
