from procesamiento import (
    cargar_json,
    normalizar_inventario,
    normalizar_vendedores,
    procesar_ventas,
    generar_resumen_vendedores,
    ordenar_ventas
)
from exportacion import (
    exportar_ventas_por_vendedor,
    exportar_ventas_rechazadas,
    exportar_resumen_vendedores,
    exportar_inventario_actualizado
)
from pruebas import ejecutar_pruebas


def mostrar_informe_procesamiento(ventas_validas, ventas_rechazadas, resumen_vendedores):
    print("\n" + "=" * 60)
    print("VENTAS RECHAZADAS DETECTADAS")
    print("=" * 60)
    if len(ventas_rechazadas) == 0:
        print("No hubo ventas rechazadas.")
    else:
        for rechazada in ventas_rechazadas:
            print(
                f"-> Venta #{rechazada['id_venta']} ({rechazada['fecha']}) "
                f"| Vendedor: {rechazada['id_vendedor']} | Motivo: {rechazada['motivo']}"
            )

    print("\n" + "=" * 60)
    print("RESUMEN POR VENDEDOR ACTIVO")
    print("=" * 60)
    for item in resumen_vendedores:
        print(
            f"-> [{item['id_vendedor']}] {item['nombre']}: "
            f"{item['cantidad_ventas']} ventas | "
            f"{item['unidades_vendidas']} unidades | "
            f"Total: ${item['total_vendido']}"
        )

    print("-" * 60)
    print(f"Total ventas válidas:    {len(ventas_validas)}")
    print(f"Total ventas rechazadas: {len(ventas_rechazadas)}")
    print("=" * 60)


def pedir_opciones_usuario():
    print("\n--- CONFIGURACIÓN DE REPORTES CSV ---")

    while True:
        separador = input("Ingrese el separador para los CSV (',' o ';'): ").strip()
        if separador in [",", ";"]:
            break
        print("Error: Debe ingresar ',' o ';'.")

    while True:
        criterio = input("Ordenar ventas por (fecha, total, id_venta): ").strip().lower()
        if criterio in ["fecha", "total", "id_venta"]:
            break
        print("Error: Ingrese 'fecha', 'total' o 'id_venta'.")

    while True:
        sentido = input("Sentido del orden (asc / desc): ").strip().lower()
        if sentido in ["asc", "desc"]:
            break
        print("Error: Ingrese 'asc' para ascendente o 'desc' para descendente.")

    descendente = (sentido == "desc")
    return separador, criterio, descendente


def main():
    print("\n" + "=" * 60)
    print("   SISTEMA DE PROCESAMIENTO DE VENTAS E INVENTARIO")
    print("=" * 60)

    ejecutar_pruebas()
    print("[OK] Pruebas internas verificadas correctamente.")

    datos_inventario = cargar_json("inventario.json")
    datos_ventas = cargar_json("ventas.json")
    if datos_inventario is None or datos_ventas is None:
        print("No se pudo continuar por falta de archivos de entrada.")
        return

    productos = normalizar_inventario(datos_inventario)
    vendedores = normalizar_vendedores(datos_ventas.get("vendedores", []))
    ventas_crudas = datos_ventas.get("ventas", [])

    ventas_validas, ventas_rechazadas = procesar_ventas(ventas_crudas, vendedores, productos)
    resumen_vendedores = generar_resumen_vendedores(vendedores, ventas_validas)

    mostrar_informe_procesamiento(ventas_validas, ventas_rechazadas, resumen_vendedores)

    separador, criterio, descendente = pedir_opciones_usuario()
    ventas_ordenadas = ordenar_ventas(ventas_validas, criterio, descendente)

    archivos_vendedores = exportar_ventas_por_vendedor(vendedores, ventas_ordenadas, separador)
    archivo_rechazadas = exportar_ventas_rechazadas(ventas_rechazadas, separador)
    archivo_resumen = exportar_resumen_vendedores(resumen_vendedores, separador)
    fecha_act = datos_inventario.get("fecha_actualizacion", "")
    archivo_inventario = exportar_inventario_actualizado(fecha_act, productos)

    print("\n" + "=" * 60)
    print("ARCHIVOS GENERADOS EXITOSAMENTE")
    print("=" * 60)
    for nombre in archivos_vendedores:
        print(f"-> {nombre}")
    print(f"-> {archivo_rechazadas}")
    print(f"-> {archivo_resumen}")
    print(f"-> {archivo_inventario}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()