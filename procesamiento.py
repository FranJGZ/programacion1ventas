import json


def cargar_json(ruta_archivo):
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{ruta_archivo}'.")
        return None
    except json.JSONDecodeError:
        print(f"Error: El archivo '{ruta_archivo}' no tiene un formato JSON válido.")
        return None


def aplanar_ventas(estructura):
    # Se utiliza recursividad porque las ventas pueden venir anidadas en múltiples niveles de listas
    ventas_planas = []
    for elemento in estructura:
        if isinstance(elemento, list):
            ventas_planas.extend(aplanar_ventas(elemento))
        else:
            ventas_planas.append(elemento)
    return ventas_planas


def normalizar_inventario(datos_inventario):
    productos_normalizados = []
    for prod in datos_inventario.get("productos", []):
        categoria = prod.get("categoria")
        if categoria is None or str(categoria).strip() == "":
            categoria_limpia = "Sin categoría"
        else:
            categoria_limpia = str(categoria).strip()

        producto_limpio = {
            "id": int(prod["id"]),
            "nombre": str(prod["nombre"]).strip(),
            "categoria": categoria_limpia,
            "precio": float(prod["precio"]),
            "stock": int(prod["stock"]),
            "activo": bool(prod.get("activo", False))
        }
        productos_normalizados.append(producto_limpio)

    return productos_normalizados


def normalizar_vendedores(lista_vendedores):
    vendedores_normalizados = []
    for vend in lista_vendedores:
        vendedor_limpio = {
            "id": int(vend["id"]),
            "nombre": str(vend["nombre"]).strip(),
            "activo": bool(vend.get("activo", False))
        }
        vendedores_normalizados.append(vendedor_limpio)
    return vendedores_normalizados


def validar_cantidad(valor):
    # En Python bool es subclase de int, por lo que se descarta explícitamente
    if valor is None or isinstance(valor, bool):
        return False, 0, "Cantidad vacía o no numérica"

    if isinstance(valor, float):
        return False, 0, "Cantidad decimal no permitida"

    if isinstance(valor, str):
        texto = valor.strip()
        if texto == "":
            return False, 0, "Cantidad vacía"
        if "." in texto or "," in texto:
            return False, 0, "Cantidad decimal no permitida"
        try:
            cantidad = int(texto)
        except ValueError:
            return False, 0, "Cantidad no numérica"
    elif isinstance(valor, int):
        cantidad = valor
    else:
        return False, 0, "Cantidad inválida"

    if cantidad <= 0:
        return False, 0, "Cantidad igual a cero o negativa"

    return True, cantidad, ""


def calcular_montos(subtotal):
    subtotal = round(float(subtotal), 2)

    if subtotal < 100000:
        porcentaje_descuento = 0
    elif subtotal < 300000:
        porcentaje_descuento = 5
    else:
        porcentaje_descuento = 10

    descuento = round(subtotal * (porcentaje_descuento / 100), 2)
    total = round(subtotal - descuento, 2)

    return subtotal, porcentaje_descuento, descuento, total


def registrar_rechazo(id_venta, fecha, id_vendedor, motivo):
    return {
        "id_venta": id_venta,
        "fecha": fecha,
        "id_vendedor": id_vendedor,
        "motivo": motivo
    }


def procesar_ventas(ventas_crudas, vendedores, productos_inventario):
    lista_ventas = aplanar_ventas(ventas_crudas)

    # Diccionarios de búsqueda rápida por ID para relacionar vendedores y productos
    mapa_vendedores = {}
    for v in vendedores:
        mapa_vendedores[v["id"]] = v

    mapa_productos = {}
    for p in productos_inventario:
        mapa_productos[p["id"]] = p

    ventas_validas = []
    ventas_rechazadas = []
    ids_ventas_procesados = []

    for venta in lista_ventas:
        fecha = str(venta.get("fecha", "")).strip()

        try:
            id_venta = int(venta.get("id_venta"))
        except (ValueError, TypeError):
            id_venta = venta.get("id_venta")
            ventas_rechazadas.append(registrar_rechazo(id_venta, fecha, venta.get("id_vendedor"), "ID de venta inválido"))
            continue

        try:
            id_vendedor = int(venta.get("id_vendedor"))
        except (ValueError, TypeError):
            id_vendedor = venta.get("id_vendedor")
            ventas_rechazadas.append(registrar_rechazo(id_venta, fecha, id_vendedor, "Vendedor inexistente"))
            continue

        # 1. Verificar ID de venta repetido
        if id_venta in ids_ventas_procesados:
            ventas_rechazadas.append(registrar_rechazo(id_venta, fecha, id_vendedor, "ID de venta repetido"))
            continue
        ids_ventas_procesados.append(id_venta)

        # 2. Verificar existencia y estado del vendedor
        if id_vendedor not in mapa_vendedores:
            ventas_rechazadas.append(registrar_rechazo(id_venta, fecha, id_vendedor, "Vendedor inexistente"))
            continue
        if not mapa_vendedores[id_vendedor]["activo"]:
            ventas_rechazadas.append(registrar_rechazo(id_venta, fecha, id_vendedor, "Vendedor inactivo"))
            continue

        # 3. Verificar que la lista de productos no esté vacía
        items = venta.get("items", [])
        if not isinstance(items, list) or len(items) == 0:
            ventas_rechazadas.append(registrar_rechazo(id_venta, fecha, id_vendedor, "Lista de productos vacía"))
            continue

        # 4. Validar todos los ítems antes de descontar stock para no alterar el inventario si la venta falla
        productos_en_esta_venta = []
        items_validados = []
        motivo_error = ""

        for item in items:
            try:
                id_prod = int(item.get("id_producto"))
            except (ValueError, TypeError):
                motivo_error = "Producto inexistente"
                break

            if id_prod not in mapa_productos:
                motivo_error = f"Producto {id_prod} inexistente"
                break

            producto_actual = mapa_productos[id_prod]
            if not producto_actual["activo"]:
                motivo_error = f"Producto {id_prod} inactivo"
                break

            if id_prod in productos_en_esta_venta:
                motivo_error = f"Producto {id_prod} repetido dentro de la misma venta"
                break
            productos_en_esta_venta.append(id_prod)

            es_valida, cantidad, error_cant = validar_cantidad(item.get("cantidad"))
            if not es_valida:
                motivo_error = error_cant
                break

            if cantidad > producto_actual["stock"]:
                motivo_error = f"Stock insuficiente para el producto {id_prod}"
                break

            items_validados.append((producto_actual, cantidad))

        if motivo_error != "":
            ventas_rechazadas.append(registrar_rechazo(id_venta, fecha, id_vendedor, motivo_error))
            continue

        # 5. Si toda la venta es válida, actualizar el stock y calcular totales
        unidades_totales = 0
        subtotal_bruto = 0.0

        for producto_actual, cantidad in items_validados:
            producto_actual["stock"] -= cantidad
            unidades_totales += cantidad
            subtotal_bruto += producto_actual["precio"] * cantidad

        subtotal, porcentaje_dto, descuento, total = calcular_montos(subtotal_bruto)

        venta_procesada = {
            "id_venta": id_venta,
            "fecha": fecha,
            "id_vendedor": id_vendedor,
            "cantidad_productos": len(items_validados),
            "unidades": unidades_totales,
            "subtotal": subtotal,
            "porcentaje_descuento": porcentaje_dto,
            "descuento": descuento,
            "total": total
        }
        ventas_validas.append(venta_procesada)

    return ventas_validas, ventas_rechazadas


def generar_resumen_vendedores(vendedores, ventas_validas):
    resumen = []
    for vendedor in vendedores:
        if not vendedor["activo"]:
            continue

        id_vend = vendedor["id"]
        cant_ventas = 0
        unidades_vendidas = 0
        total_vendido = 0.0

        for venta in ventas_validas:
            if venta["id_vendedor"] == id_vend:
                cant_ventas += 1
                unidades_vendidas += venta["unidades"]
                total_vendido += venta["total"]

        resumen.append({
            "id_vendedor": id_vend,
            "nombre": vendedor["nombre"],
            "cantidad_ventas": cant_ventas,
            "unidades_vendidas": unidades_vendidas,
            "total_vendido": round(total_vendido, 2)
        })

    return resumen


def ordenar_ventas(ventas, criterio, descendente):
    if criterio == "fecha":
        return sorted(ventas, key=lambda v: v["fecha"], reverse=descendente)
    elif criterio == "total":
        return sorted(ventas, key=lambda v: v["total"], reverse=descendente)
    elif criterio == "id_venta":
        return sorted(ventas, key=lambda v: v["id_venta"], reverse=descendente)
    return ventas
