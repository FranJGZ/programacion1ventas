"""
Módulo para la carga de datos JSON y aplanamiento de estructuras anidadas.
"""

import json
import os
from typing import Any, Dict, List


def load_json_data(file_path: str) -> Dict[str, Any]:
    """
    Carga y decodifica un archivo JSON con codificación UTF-8.

    Args:
        file_path: Ruta al archivo JSON.

    Returns:
        Diccionario con los datos deserializados del archivo.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        json.JSONDecodeError: Si el archivo no tiene un formato JSON válido.
        ValueError: Si la estructura raíz no es un diccionario.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No se encontró el archivo: '{file_path}'")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("El archivo JSON debe tener un objeto raíz (diccionario).")

    return data


def flatten_products(raw_items: List[Any]) -> List[Any]:
    """
    Aplana de forma recursiva una lista heterogénea que puede contener
    diccionarios de productos o sublistas anidadas de productos.

    Args:
        raw_items: Lista original que puede contener listas anidadas.

    Returns:
        Lista unidimensional con todos los elementos individuales.
    """
    flat_list = []
    for item in raw_items:
        if isinstance(item, list):
            # Llamada recursiva para resolver sublistas anidadas
            flat_list.extend(flatten_products(item))
        else:
            flat_list.append(item)
    return flat_list
