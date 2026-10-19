"""
Módulo para la exportación de datos a archivos CSV utilizando csv.DictWriter.
"""

import csv
import os
from typing import Any, Dict, List
from constants import (
    REJECTED_CSV_COLUMNS,
    REJECTED_CSV_FILENAME,
    USER_CSV_COLUMNS,
    USER_CSV_TEMPLATE
)


def export_user_csv(
    user_id: int,
    products: List[Dict[str, Any]],
    delimiter: str = ",",
    output_dir: str = "."
) -> str:
    """
    Exporta la lista de productos válidos de un usuario a un archivo CSV.

    Columnas estrictas:
        id, nombre, categoria, precio, stock

    Args:
        user_id: Identificador del usuario.
        products: Lista de productos ordenados y normalizados.
        delimiter: Separador a utilizar (',' o ';').
        output_dir: Directorio donde se guardará el archivo.

    Returns:
        Ruta del archivo generado.
    """
    filename = USER_CSV_TEMPLATE.format(user_id=user_id)
    file_path = os.path.join(output_dir, filename)

    with open(file_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=USER_CSV_COLUMNS,
            delimiter=delimiter,
            extrasaction="ignore",
            quoting=csv.QUOTE_MINIMAL
        )
        writer.writeheader()
        writer.writerows(products)

    return file_path


def export_rejected_csv(
    rejected_products: List[Dict[str, Any]],
    delimiter: str = ",",
    output_dir: str = "."
) -> str:
    """
    Exporta la lista de productos rechazados con su motivo a 'productos_rechazados.csv'.

    Columnas estrictas:
        id, nombre, motivo

    Args:
        rejected_products: Lista de diccionarios con 'id', 'nombre' y 'motivo'.
        delimiter: Separador a utilizar (',' o ';').
        output_dir: Directorio donde se guardará el archivo.

    Returns:
        Ruta del archivo generado.
    """
    file_path = os.path.join(output_dir, REJECTED_CSV_FILENAME)

    with open(file_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=REJECTED_CSV_COLUMNS,
            delimiter=delimiter,
            extrasaction="ignore",
            quoting=csv.QUOTE_MINIMAL
        )
        writer.writeheader()
        writer.writerows(rejected_products)

    return file_path
