import Py3PDF as pdf
import os

def extraer_paginas(pdf_path, paginas, output_dir):
    
    with open(pdf_path, 'rb') as file:
        pdf_reader = pdf.PdfReader(file)
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for pagina in paginas:
            if pagina <= len(pdf_reader.pages):
                pagina_obj = pdf_reader.pages[pagina - 1]
                
                output_path = os.path.join(output_dir, f'pagina_{pagina}.pdf')
                
                pdf_writer = pdf.PdfWriter()
                pdf_writer.add_page(pagina_obj)

                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)
                print(f'Página {pagina} extraída y guardada en {output_path}')
            else:
                print(f'La página {pagina} no existe en el PDF.')
                
if __name__== "__main__":
    ruta_pdf = r'C:\Users\jgmeras\Documents\Python Scripts\Aplicaciones\Utilidades\prueba.pdf'
    paginas_a_extraer = [1, 2, 3]
    carpeta_salida = r'C:\Users\jgmeras\Documents\Python Scripts\Aplicaciones\Utilidades\salida'
    
    extraer_paginas(ruta_pdf, paginas_a_extraer, carpeta_salida)