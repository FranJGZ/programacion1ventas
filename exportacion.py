import csv
import json


def exportar_ventas_por_vendedor(vendedores, ventas_ordenadas, separador):
    columnas = [
        "id_venta",
        "fecha",
        "cantidad_productos",
        "unidades",
        "subtotal",
        "porcentaje_descuento",
        "descuento",
        "total"
    ]
    archivos_generados = []

    for vendedor in vendedores:
        if not vendedor["activo"]:
            continue

        id_vendedor = vendedor["id"]
        filas_vendedor = []

        for venta in ventas_ordenadas:
            if venta["id_vendedor"] == id_vendedor:
                filas_vendedor.append({
                    "id_venta": venta["id_venta"],
                    "fecha": venta["fecha"],
                    "cantidad_productos": venta["cantidad_productos"],
                    "unidades": venta["unidades"],
                    "subtotal": venta["subtotal"],
                    "porcentaje_descuento": venta["porcentaje_descuento"],
                    "descuento": venta["descuento"],
                    "total": venta["total"]
                })

        nombre_archivo = f"ventas_{id_vendedor}.csv"
        with open(nombre_archivo, mode="w", newline="", encoding="utf-8") as archivo:
            writer = csv.DictWriter(archivo, fieldnames=columnas, delimiter=separador)
            writer.writeheader()
            writer.writerows(filas_vendedor)

        archivos_generados.append(nombre_archivo)

    return archivos_generados


def exportar_ventas_rechazadas(ventas_rechazadas, separador):
    columnas = ["id_venta", "fecha", "id_vendedor", "motivo"]
    nombre_archivo = "ventas_rechazadas.csv"

    with open(nombre_archivo, mode="w", newline="", encoding="utf-8") as archivo:
        writer = csv.DictWriter(archivo, fieldnames=columnas, delimiter=separador)
        writer.writeheader()
        writer.writerows(ventas_rechazadas)

    return nombre_archivo


def exportar_resumen_vendedores(resumen_vendedores, separador):
    columnas = ["id_vendedor", "nombre", "cantidad_ventas", "unidades_vendidas", "total_vendido"]
    nombre_archivo = "resumen_vendedores.csv"

    with open(nombre_archivo, mode="w", newline="", encoding="utf-8") as archivo:
        writer = csv.DictWriter(archivo, fieldnames=columnas, delimiter=separador)
        writer.writeheader()
        writer.writerows(resumen_vendedores)

    return nombre_archivo


def exportar_inventario_actualizado(fecha_actualizacion, productos_actualizados):
    nombre_archivo = "inventario_actualizado.json"
    datos_salida = {
        "fecha_actualizacion": fecha_actualizacion,
        "productos": productos_actualizados
    }

    # ensure_ascii=False permite conservar tildes y caracteres especiales
    with open(nombre_archivo, mode="w", encoding="utf-8") as archivo:
        json.dump(datos_salida, archivo, indent=2, ensure_ascii=False)

    return nombre_archivo
