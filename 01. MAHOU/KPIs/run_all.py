import inb_out
import inb_out_cajas
import qry_transport_Fact
import roturas_stock

fecha_inicio = input("Introducir fecha inicio (YYYY-MM-DD): ")
fecha_fin = input("Introducir fecha fin (YYYY-MM-DD): ")

roturas_stock.qry_inb_out(
    fecha_inicio,
    fecha_fin)

inb_out.qry_inb_out(
    fecha_inicio,
    fecha_fin)

inb_out_cajas.qry_inb_out(
    fecha_inicio,
    fecha_fin)

print("✅ Todos los archivos generados correctamente")