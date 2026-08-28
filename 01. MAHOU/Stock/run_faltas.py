import qry_pedidos_final_steel
import descarga_edi_steel
import qry_consulta_UBSPROD
import cruce_pedidos
import view_1_order
import fcp_pedidos_excel

import os
import pandas as pd
from sqlalchemy import create_engine, text
from tabulate import tabulate

import shutil

from pyfiglet import Figlet
from rich.console import Console
from rich.panel import Panel
from rich.align import Align



user = os.getenv("USERNAME")
path = os.getcwd()

console = Console()

DB_FILE = f"{path}\\apoyo.db"

import shutil
from tabulate import tabulate


def acortar_texto(valor, max_len):
    valor = "" if valor is None else str(valor)

    if len(valor) <= max_len:
        return valor

    if max_len <= 3:
        return valor[:max_len]

    return valor[:max_len - 3] + "..."

def imprimir_articulo_vertical(df):
    """
    Imprime un único artículo en formato vertical.
    Se usa cuando la tabla no cabe en pantalla.
    """

    if df.empty:
        print("No hay datos para mostrar.")
        return

    fila = df.iloc[0]

    ancho_columna = max(len(str(columna)) for columna in fila.index) + 2

    print("\n" + "-" * 60)

    for columna, valor in fila.items():
        print(f"{columna:<{ancho_columna}}: {valor}")

    print("-" * 60)

def imprimir_df_ajustado(df):
    """
    Intenta imprimir el DataFrame como tabla ajustada al ancho real de pantalla.
    Si no cabe, pasa automáticamente a formato vertical.
    """

    if df.empty:
        print("No se encontraron datos.")
        return

    ancho_terminal = shutil.get_terminal_size(fallback=(160, 40)).columns
    ancho_maximo = ancho_terminal - 2

    df_base = df.copy()

    # Probamos de más ancho a menos ancho para la descripción
    for ancho_desc in range(80, 9, -5):

        df_temp = df_base.copy()

        if "Descripcion" in df_temp.columns:
            df_temp["Descripcion"] = df_temp["Descripcion"].apply(
                lambda x: acortar_texto(x, ancho_desc)
            )

        tabla = tabulate(
            df_temp,
            headers="keys",
            tablefmt="grid",
            showindex=False,
            stralign="left",
            numalign="left"
        )

        ancho_tabla = max(len(linea) for linea in tabla.splitlines())

        # Si quieres probar:
        # print(f"Terminal: {ancho_terminal} | Tabla: {ancho_tabla} | Desc: {ancho_desc}")

        if ancho_tabla <= ancho_maximo:
            print(tabla)
            return

    # Si no cabe ni recortando descripción, formato vertical
    imprimir_articulo_vertical(df)

def imprimir_df_inteligente(df):
    """
    Función wrapper.
    Primero intenta tabla. Si no cabe, imprimir_df_ajustado ya pasa a vertical.
    """

    imprimir_df_ajustado(df)

def limpiar_pantalla():
    os.system("cls" if os.name == "nt" else "clear")

def esperar_enter():
    input("\nPresione Enter para continuar...")
    limpiar_pantalla()

def cabecera(num):
    f = Figlet(font="slant")
    print("\n"+ "-"*80)
    print(f.renderText("MAHOU"))
    print(f"PASO {num}".center(80, "-"))

def mostrar_titulo():
    f = Figlet(font="small")
    ascii_titulo = f.renderText("MAHOU")

    contenido = Align.center(
        f"[bold cyan]{ascii_titulo}[/bold cyan]\n"
        "[bold white]FALTAS ARTÍCULOS Y MAESTRO[/bold white]"
    )

    console.print(Panel(contenido, border_style="cyan"))

def convertir_tipo(valor, tipo):
    """
    Convierte valores de pandas/numpy a tipos nativos de Python
    antes de enviarlos a SQLite.
    """

    if valor is None:
        return None

    # Por si viene un BLOB de SQLite por el problema del numpy.int64
    if isinstance(valor, (bytes, bytearray)):
        try:
            valor = int.from_bytes(valor, byteorder="little", signed=True)
        except Exception:
            valor = valor.decode(errors="ignore")

    # Control de nulos de pandas/numpy
    try:
        if pd.isna(valor):
            return None
    except Exception:
        pass

    if tipo == "float":
        return float(valor) #type:ignore

    elif tipo == "int":
        return int(float(valor)) #type:ignore

    elif tipo == "bool":
        if isinstance(valor, str):
            valor_txt = valor.strip().upper()

            if valor_txt in ["SI", "S", "1", "TRUE", "T"]:
                return 1

            if valor_txt in ["NO", "N", "0", "FALSE", "F"]:
                return 0

        return 1 if int(float(valor)) == 1 else 0 #type:ignore

    else:
        return str(valor)

def pedir_valor(nombre_campo, valor_actual, tipo):
    """
    Pide un valor por consola.
    Si se pulsa Enter, devuelve el valor actual sin modificar,
    pero convertido a tipo nativo de Python.
    """

    valor_actual_convertido = convertir_tipo(valor_actual, tipo)

    while True:

        if tipo == "bool":
            valor_mostrado = "SI" if valor_actual_convertido == 1 else "NO"
        else:
            valor_mostrado = "" if valor_actual_convertido is None else valor_actual_convertido

        entrada = input(f"{nombre_campo} [{valor_mostrado}]: ").strip()

        # Enter: mantiene valor, pero ya convertido a int/float/bool nativo
        if entrada == "":
            return valor_actual_convertido

        try:
            if tipo == "float":
                return float(entrada.replace(",", "."))

            elif tipo == "int":
                return int(float(entrada.replace(",", ".")))

            elif tipo == "bool":
                entrada = entrada.upper()

                if entrada in ["SI", "S", "1"]:
                    return 1

                elif entrada in ["NO", "N", "0"]:
                    return 0

                else:
                    print("Valor no válido. Introduce SI o NO.")

            else:
                return entrada

        except ValueError:
            print("Valor no válido. Inténtalo de nuevo.")

def selector_tarea():
    limpiar_pantalla()
    while True:

        mostrar_titulo()

        print("\nElige:")
        print("       (1) Sacar archivo de faltas")
        print("       (2) Revisar un código")
        print("       (3) Actualizar un código")
        print("       (4) Actualizar todo el maestro")
        print("       (5) Comprobar FCP de un pedido")
        print("       (6) Comprobar FCP a traves del excel")
        print("       (7) Salir")

        opcion = input("\n(1) - (7): ").strip()

        if opcion == "1":
            fichero_faltas()
            esperar_enter()

        elif opcion == "2":
            revisar_codigo()
            esperar_enter()

        elif opcion == "3":
            update_codigo()
            esperar_enter()

        elif opcion == "4":
            update_maestro()
            esperar_enter()

        elif opcion == "5":
            comprobar_1_fcp()
            esperar_enter()

        elif opcion == "6":
            leer_excel_muestra()
            esperar_enter()
        

        elif opcion == "7":
            print("\n"+ "*"*50 +"\nSaliendo del programa...\n"+ "*"*50 + "\n")
            break

        else:
            print("\nOpción incorrecta, escoja 1 a 7")

def comprobar_1_fcp():
    pedido = input("\nIntroduce el número de pedido: ")
    
    view_1_order.inspect_edi(pedido)

def leer_excel_muestra():
    fcp_pedidos_excel.procesar_archivo_muestra()

def leer_csv(ruta_archivo):
    """
    Lee un archivo Excel y devuelve un DataFrame.
    """
    try:
        #leemos solo la columna A
        df = pd.read_csv(ruta_archivo, sep=";", encoding="utf-8-sig", dtype=str, usecols=["Albarán"])
        df["Albarán"] = df["Albarán"].fillna("").str.strip()

        
        df = (
            df[df["Albarán"] != ""][["Albarán"]]
            .drop_duplicates()
)

        #Eliminamos filas vacias y resetear índice
        df = df.dropna().reset_index(drop=True)
                
        return df
    except Exception as e:
        print(f"Error al leer el archivo {ruta_archivo}: {e}")
        return None

def revisar_codigo():
    
    codigo = str(input("\nIntroducir código a buscar: "))

    engine_sqlite = create_engine(f"sqlite:///{DB_FILE}")
    query = text("""SELECT 
                        CodigoProdClte AS [Referencia], NombreProdClte AS [Descripcion], PesoBrutoProdClte AS [Peso],
                        VolumenBrutoProdClte AS [Volumen], CASE WHEN ConvertirPaletACajaProdClte = 1 THEN 'SI' ELSE 'NO'END AS [Hijo], CodigoUnidad AS [Tipo],
                         CajasPaletProdClte AS [Cajas Palet], AltoPaletProdClte AS [Alto Palet], AnchoPaletProdClte AS [Ancho Palet], LargoPaletProdClte AS [Largo Palet],
                        CapasPaletProdClte AS [Capas Palet],DiasFechaProdClte AS [Días Prod(Corto)], DiasCaducidadProdClte AS [Días Caducidad(Largo)]
                    FROM
                        maestro_msm
                    WHERE
                        TRIM(CodigoProdClte) = TRIM(:codigo)
                 
                 """)

    df_maestro = pd.read_sql(query, engine_sqlite, params={"codigo": codigo})
    print("\n")
    
    imprimir_df_inteligente(df_maestro)

    engine_sqlite.dispose()
    print("\n" + "*" * 50 + "\n")

def salida_elegante():
    print("\n\n" + "*" * 50)
    print("Proceso cancelado por el usuario.")
    print("Saliendo del programa...")
    print("*" * 50 + "\n")

def update_codigo():

    engine_sqlite = create_engine(f"sqlite:///{DB_FILE}")

    codigo = input("\nIngrese código: ").strip()

    # Campos que queremos editar:
    # campo en BBDD, texto mostrado al usuario, tipo de dato
    campos = [
        ("PesoBrutoProdClte", "Peso", "float"),
        ("VolumenBrutoProdClte", "Volumen", "float"),
        ("ConvertirPaletACajaProdClte", "Convertir a caja", "bool"),
        ("CodigoUnidad", "Tipo", "str"),
        ("CajasPaletProdClte", "Cajas Palet", "int"),
        ("AltoPaletProdClte", "Alto Palet", "float"),
        ("AnchoPaletProdClte", "Ancho Palet", "float"),
        ("LargoPaletProdClte", "Largo Palet", "float"),
        ("CapasPaletProdClte", "Capas Palet", "int"),
        ("DiasFechaProdClte", "Días Fecha Prod(Corto)", "int"),
        ("DiasCaducidadProdClte", "Días Caducidad(Largo)", "int"),
    ]

    # Montamos el SELECT con los campos necesarios
    columnas_select = [
        "CodigoProdClte",
        "NombreProdClte"
    ] + [campo_bd for campo_bd, _, _ in campos]

    query_select = text(f"""
        SELECT
            {", ".join(columnas_select)}
        FROM maestro_msm
        WHERE TRIM(CodigoProdClte) = TRIM(:codigo)
    """)

    df = pd.read_sql(
        query_select,
        engine_sqlite,
        params={"codigo": codigo}
    )

    if df.empty:
        print("\nArtículo no encontrado.")
        return

    articulo = df.iloc[0]

    print("\nARTÍCULO ENCONTRADO")
    print("-" * 50)
    print(f"Referencia : {articulo['CodigoProdClte']}")
    print(f"Descripción: {articulo['NombreProdClte']}")
    print("-" * 50)
    print("Pulsa Enter para mantener el valor actual.")
    print()

    valores_actualizados = {}

    for campo_bd, nombre_mostrar, tipo in campos:

        valor_actual = articulo[campo_bd]

       

        nuevo_valor = pedir_valor(
            nombre_mostrar,
            valor_actual,
            tipo
        )

        #print(f"DEBUG DESPUÉS -> {campo_bd}: {nuevo_valor} ({type(nuevo_valor)})")

        valores_actualizados[campo_bd] = nuevo_valor

    # Generamos dinámicamente:
    # PesoBrutoProdClte = :PesoBrutoProdClte,
    # VolumenBrutoProdClte = :VolumenBrutoProdClte, etc.
    set_clause = ",\n            ".join(
        f"{campo_bd} = :{campo_bd}"
        for campo_bd, _, _ in campos
    )

    query_update = text(f"""
        UPDATE maestro_msm
        SET
            {set_clause}
        WHERE TRIM(CodigoProdClte) = TRIM(:codigo)
    """)

    valores_actualizados["codigo"] = codigo

    with engine_sqlite.begin() as conn:
        conn.execute(query_update, valores_actualizados)

    print("\nArtículo actualizado correctamente.")
    print("\n" + "*" * 50 + "\n")

def update_maestro():
    
    engine_sqlserver = create_engine("mssql+pyodbc://@XGA_PROD")
    engine_sqlite = create_engine(f"sqlite:///{DB_FILE}")

    query = text("""
        SELECT 
            *
        FROM ProductosClientes
        WHERE
            ID_Cliente = 944
            
    """)

    print("\nActualizando maestro desde SQL Server...")
    print("-" * 50)

    df = pd.read_sql(query, engine_sqlserver)

    if df.empty:
        print("No se han encontrado datos en SQL Server.")
        return

    df.to_sql(
        "maestro_msm",
        engine_sqlite,
        if_exists="replace",
        index=False
    )

    print(f"Maestro actualizado correctamente. Registros cargados: {len(df)}")
    print("\n" + "*" * 50 + "\n")

def fichero_faltas():

    num = 1

    print("\n")
    fecha_inicio = input("Introducir fecha inicio (YYYY-MM-DD): ")
    fecha_fin = input("Introducir fecha fin (YYYY-MM-DD): ")
    while True:
        almacen = input("Elige (1) Steel o (2) Interim: ")
        if almacen == "1":
            selector_almacen = 221
            break
        if almacen == "2":
            selector_almacen = 129
            break
        else:
            print("\n Opción incorrecta, escoja 1 (Steel) o 2 (Interim)")

    if selector_almacen == 221:
        nombre_almacen = "Steel"
    if selector_almacen == 129:
        nombre_almacen = "Interim"

    print("\n")
    print("=".center(50, "="))
    print("MAHOU FALTAS".center(50, "-"))
    print("=".center(50, "="))
    print("\n")
    print(f"Procesando fechas {fecha_inicio} a {fecha_fin} para el almacén {nombre_almacen}")

    print("\n")
    cabecera(num)
    num = num + 1

    print("\nComenzando con busqueda de pedidos integrados\n")
    nombre_archivo = qry_pedidos_final_steel.consulta_pedidos(fecha_inicio, fecha_fin, selector_almacen)
    #print(nombre_archivo)
    print(f"Archivo de pedidos integrados generado")
    path_file = f"{path}\\{nombre_archivo}"

    print("\n")
    cabecera(num)
    num = num + 1

    print("\nComenzando descarga y lectura de EDIs\n")
    df = leer_csv(path_file)
    #print(df)
    parsed_edis = descarga_edi_steel.descargar_edi(df, selector_almacen)
    print("\nProcesado EDIs descargados\n")

    #print("parsed_edis devuelto:", parsed_edis)

    if parsed_edis is None:
        raise ValueError(
            "descarga_edi_steel.descargar_edi() ha devuelto None. "
            "Revisa que esa función haga return output_file."
        )

    print("\n")
    cabecera(num)
    num = num + 1


    print("\nGenerando fichero de stock\n")
    nombre_stock = qry_consulta_UBSPROD.ejecutar_qry(fecha_inicio, fecha_fin, selector_almacen)

    print("\n")
    cabecera(num)
    num = num + 1

    print("\nGenerando archivo de faltas\n")
    cruce_pedidos.cruce_archivos(nombre_archivo, parsed_edis, nombre_stock, selector_almacen)

    print("\n")
    print("=".center(50, "=")+"\n")
    print("Proceso completado".center(50, "-"))
    print("\n")
    print("=".center(50, "="))

if __name__ == "__main__":
    try:
        selector_tarea()
    except KeyboardInterrupt:
        salida_elegante()

