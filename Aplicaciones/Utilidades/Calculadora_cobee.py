


def calcular_ahorro(bruto, irpf, ss, gasto):
    """_summary_

    Args:
        bruto (_int_): _sueldo bruto mensual_
        irpf (_int_): _porcentaje IRPF_
        ss (_int_): _Porcentaje SS_
        gasto (_int_): _gasto mensual a comparar_
    """
    neto_normal = bruto * (1-ss) * (1-irpf) - gasto
    
    neto_beneficio = (bruto - gasto) * (1-ss) * (1-irpf)
    
    ahorro = neto_beneficio - neto_normal
    
    return ahorro, neto_normal, neto_beneficio
    
bruto = int(input("Ingrese sueldo bruto: "))
irpf = float(input("Ingrese IRPF (Ej: 0.15 para 15%): "))
ss = float(input("Ingrese SS(Ej: 0.06 para 6%): "))
gasto = int(input("Ingrese gasto mensual: "))

ahorro, normal, beneficio = calcular_ahorro(bruto, irpf, ss, gasto)

print(f"Neto sin beneficio: {normal:.2f}€")
print(f"Neto con beneficio: {beneficio:.2f}€")
print(f"Ahorro mensual: {ahorro:.2f}€")
print(f"Ahorro anual: {ahorro*12:.2f}€")