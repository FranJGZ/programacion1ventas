"""
Módulo de validación, limpieza y normalización de productos.
"""

from typing import Any, Dict, List, Optional, Set, Tuple
from constants import DEFAULT_CATEGORY


def clean_string(value: Optional[str]) -> str:
    """
    Elimina espacios en blanco sobrantes al inicio, final e intermedios excesivos.
    """
    if value is None:
        return ""
    # Eliminar espacios iniciales/finales y colapsar espacios múltiples internos
    return " ".join(str(value).strip().split())


def normalize_numeric_fields(
    raw_id: Any,
    raw_precio: Any,
    raw_stock: Any
) -> Tuple[int, float, int]:
    """
    Valida y convierte los campos numéricos a sus tipos correspondientes:
    - id: int
    - precio: float (o float redondeado a 2 decimales)
    - stock: int

    Raises:
        ValueError: Si algún valor no es convertible o es negativo.
    """
    # Validación de ID
    if raw_id is None or str(raw_id).strip() == "":
        raise ValueError("El ID del producto es obligatorio y no puede estar vacío.")
    try:
        norm_id = int(raw_id)
    except (ValueError, TypeError):
        raise ValueError(f"El ID '{raw_id}' no es un número entero válido.")
    if norm_id <= 0:
        raise ValueError(f"El ID {norm_id} debe ser un entero positivo mayor a 0.")

    # Validación de Precio
    if raw_precio is None or str(raw_precio).strip() == "":
        raise ValueError("Dato faltante: el precio no puede ser nulo o vacío.")
    try:
        norm_precio = float(raw_precio)
    except (ValueError, TypeError):
        raise ValueError(f"Dato incorrecto: el precio '{raw_precio}' no es un número válido.")
    if norm_precio < 0:
        raise ValueError(f"Dato incorrecto: el precio {norm_precio} no puede ser negativo.")

    # Validación de Stock
    if raw_stock is None or str(raw_stock).strip() == "":
        raise ValueError("Dato faltante: el stock no puede ser nulo o vacío.")
    try:
        norm_stock = int(raw_stock)
    except (ValueError, TypeError):
        raise ValueError(f"Dato incorrecto: el stock '{raw_stock}' no es un entero válido.")
    if norm_stock < 0:
        raise ValueError(f"Dato incorrecto: el stock {norm_stock} no puede ser negativo.")

    return norm_id, round(norm_precio, 2), norm_stock


def validate_and_process_data(
    data: Dict[str, Any],
    flat_products: List[Any]
) -> Tuple[Dict[int, List[Dict[str, Any]]], List[Dict[str, Any]]]:
    """
    Valida la lista aplanada de productos según los usuarios registrados.

    Detecta:
    1. Estructura no válida (no es diccionario).
    2. ID ausente, inválido o duplicado.
    3. Usuario inexistente en el listado de usuarios del JSON.
    4. Nombre faltante o vacío.
    5. Precio ausente, inválido o negativo.
    6. Stock ausente, inválido o negativo.

    Normaliza:
    - Campos numéricos a tipos int/float.
    - Cadenas de texto sin espacios innecesarios.
    - Categoría con valor por defecto 'Sin categoría' si falta o es nula.

    Returns:
        Una tupla con:
        - Diccionario {id_usuario: [lista de productos válidos]}
        - Lista de diccionarios de productos rechazados con {'id', 'nombre', 'motivo'}
    """
    # 1. Obtener conjunto de IDs de usuarios válidos registrados
    valid_users_data = data.get("usuarios", [])
    valid_user_ids: Set[int] = set()

    for user in valid_users_data:
        if isinstance(user, dict) and "id_usuario" in user:
            try:
                valid_user_ids.add(int(user["id_usuario"]))
            except (ValueError, TypeError):
                continue

    seen_product_ids: Set[int] = set()
    valid_products_by_user: Dict[int, List[Dict[str, Any]]] = {}
    rejected_products: List[Dict[str, Any]] = []

    for item in flat_products:
        # Verificar que el elemento sea un diccionario
        if not isinstance(item, dict):
            rejected_products.append({
                "id": "N/A",
                "nombre": "Elemento inválido",
                "motivo": "El producto no tiene una estructura de datos válida (objeto/diccionario esperado)"
            })
            continue

        raw_id = item.get("id")
        raw_user_id = item.get("id_usuario")
        raw_nombre = item.get("nombre")
        raw_categoria = item.get("categoria")
        raw_precio = item.get("precio")
        raw_stock = item.get("stock")

        nombre_limpio = clean_string(raw_nombre)

        # 1. Validación del ID
        if raw_id is None or str(raw_id).strip() == "":
            rejected_products.append({
                "id": "N/A",
                "nombre": nombre_limpio or "Sin nombre",
                "motivo": "Dato faltante: el producto no posee identificador (id)"
            })
            continue

        try:
            prod_id = int(raw_id)
        except (ValueError, TypeError):
            rejected_products.append({
                "id": raw_id,
                "nombre": nombre_limpio or "Sin nombre",
                "motivo": f"Dato incorrecto: el ID '{raw_id}' no es un número entero válido"
            })
            continue

        # 2. Detección de IDs duplicados
        if prod_id in seen_product_ids:
            rejected_products.append({
                "id": prod_id,
                "nombre": nombre_limpio or "Sin nombre",
                "motivo": f"ID duplicado: el producto con ID {prod_id} ya fue registrado previamente"
            })
            continue

        # Registramos el ID visto
        seen_product_ids.add(prod_id)

        # 3. Validación de relación con usuario existente
        if raw_user_id is None or str(raw_user_id).strip() == "":
            rejected_products.append({
                "id": prod_id,
                "nombre": nombre_limpio or "Sin nombre",
                "motivo": "Dato faltante: el producto no tiene asignado un id_usuario"
            })
            continue

        try:
            user_id = int(raw_user_id)
        except (ValueError, TypeError):
            rejected_products.append({
                "id": prod_id,
                "nombre": nombre_limpio or "Sin nombre",
                "motivo": f"Dato incorrecto: el id_usuario '{raw_user_id}' no es válido"
            })
            continue

        if user_id not in valid_user_ids:
            rejected_products.append({
                "id": prod_id,
                "nombre": nombre_limpio or "Sin nombre",
                "motivo": f"Relación con usuario inexistente: el usuario con ID {user_id} no existe en el sistema"
            })
            continue

        # 4. Validación de nombre
        if not nombre_limpio:
            rejected_products.append({
                "id": prod_id,
                "nombre": "Sin nombre",
                "motivo": "Dato faltante: el nombre del producto es obligatorio y no puede estar en blanco"
            })
            continue

        # 5. Validación y normalización de campos numéricos (precio y stock)
        try:
            _, norm_precio, norm_stock = normalize_numeric_fields(prod_id, raw_precio, raw_stock)
        except ValueError as err:
            rejected_products.append({
                "id": prod_id,
                "nombre": nombre_limpio,
                "motivo": str(err)
            })
            continue

        # 6. Normalización de categoría
        categoria_limpia = clean_string(raw_categoria)
        categoria_final = categoria_limpia if categoria_limpia else DEFAULT_CATEGORY

        # Producto válido y normalizado
        # Notar que respetamos exactamente las columnas requeridas para el CSV
        valid_product = {
            "id": prod_id,
            "nombre": nombre_limpio,
            "categoria": categoria_final,
            "precio": norm_precio,
            "stock": norm_stock
        }

        if user_id not in valid_products_by_user:
            valid_products_by_user[user_id] = []
        valid_products_by_user[user_id].append(valid_product)

    return valid_products_by_user, rejected_products
