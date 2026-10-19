"""
Módulo para el ordenamiento de listas de productos según criterio y dirección.
"""

from typing import Any, Dict, List


def sort_products(
    products: List[Dict[str, Any]],
    criterion: str,
    ascending: bool = True
) -> List[Dict[str, Any]]:
    """
    Ordena una lista de productos válidos según el criterio indicado.

    Args:
        products: Lista de diccionarios de productos.
        criterion: Atributo por el cual ordenar ('nombre', 'precio', 'stock').
        ascending: True para orden ascendente, False para descendente.

    Returns:
        Nueva lista con los productos ordenados.
    """
    crit = criterion.lower().strip()

    if crit == "nombre":
        key_fn = lambda x: str(x.get("nombre", "")).casefold()
    elif crit == "precio":
        key_fn = lambda x: float(x.get("precio", 0.0))
    elif crit == "stock":
        key_fn = lambda x: int(x.get("stock", 0))
    else:
        raise ValueError(
            f"Criterio de ordenamiento no válido: '{criterion}'. Opciones válidas: 'nombre', 'precio', 'stock'."
        )

    return sorted(products, key=key_fn, reverse=not ascending)
