from procesamiento import (
    aplanar_ventas,
    calcular_montos,
    validar_cantidad,
    generar_resumen_vendedores
)


def ejecutar_pruebas():
    # Prueba 1: Aplanar listas de ventas en múltiples niveles de anidamiento
    estructura_anidada = [{"id_venta": 1}, [{"id_venta": 2}, [{"id_venta": 3}]]]
    resultado_plano = aplanar_ventas(estructura_anidada)
    assert len(resultado_plano) == 3 and resultado_plano[2]["id_venta"] == 3

    # Prueba 2: Cálculo de montos sin descuento (subtotal menor a $100.000)
    subtotal, porc, desc, total = calcular_montos(50000)
    assert porc == 0 and desc == 0.0 and total == 50000.0

    # Prueba 3: Cálculo de montos con 5% de descuento (desde $100.000 hasta menos de $300.000)
    subtotal, porc, desc, total = calcular_montos(200000)
    assert porc == 5 and desc == 10000.0 and total == 190000.0

    # Prueba 4: Cálculo de montos con 10% de descuento (desde $300.000 en adelante)
    subtotal, porc, desc, total = calcular_montos(300000)
    assert porc == 10 and desc == 30000.0 and total == 270000.0

    # Prueba 5: Validación de cantidades (entero válido vs decimal, vacío o negativo)
    es_val_ok, cant_ok, _ = validar_cantidad("4")
    es_val_dec, _, _ = validar_cantidad("2.5")
    es_val_neg, _, _ = validar_cantidad(-2)
    assert es_val_ok is True and cant_ok == 4
    assert es_val_dec is False and es_val_neg is False

    # Prueba 6: Resumen de vendedores incluyendo vendedores activos sin ventas
    vendedores_prueba = [
        {"id": 101, "nombre": "Ana", "activo": True},
        {"id": 202, "nombre": "Carlos", "activo": True},
        {"id": 303, "nombre": "María", "activo": False}
    ]
    ventas_prueba = [
        {"id_vendedor": 101, "unidades": 3, "total": 150000.0}
    ]
    resumen = generar_resumen_vendedores(vendedores_prueba, ventas_prueba)
    assert len(resumen) == 2
    assert resumen[0]["cantidad_ventas"] == 1 and resumen[1]["cantidad_ventas"] == 0


if __name__ == "__main__":
    ejecutar_pruebas()
    print("Todas las pruebas con assert pasaron correctamente.")
