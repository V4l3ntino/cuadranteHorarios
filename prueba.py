def es_bisiesto(anio):
    """
    Determina si un año es bisiesto.

    Args:
    anio (int): El año a verificar.

    Returns:
    bool: True si el año es bisiesto, False en caso contrario.
    """
    # Un año es bisiesto si es divisible por 4, pero no por 100,
    # a menos que también sea divisible por 400.
    return (anio % 4 == 0) and (anio % 100 != 0) or (anio % 400 == 0)

# Ejemplos de uso:
anio_actual = 2092  # Cambia este valor por el año que quieras verificar

if es_bisiesto(anio_actual):
    print(f"El año {anio_actual} es bisiesto.")
else:
    print(f"El año {anio_actual} no es bisiesto.")

dias_meses = { 'Enero': 31, 'Febrero': 31+29, 'Marzo': 31+29+31, 'Abril': 31+29+31+30, 'Mayo': 31+29+31+30+31, 'Junio': 31+29+31+30+31+30, 'Julio': 31+29+31+30+31+30+31, 'Agosto': 31+29+31+30+31+30+31+31, 'Septiembre': 31+29+31+30+31+30+31+31+30, 'Octubre': 31+29+31+30+31+30+31+31+30+31, 'Noviembre': 31+29+31+30+31+30+31+31+30+31+30, 'Diciembre': 31+29+31+30+31+30+31+31+30+31+30+31 }

print(dias_meses["Diciembre"])