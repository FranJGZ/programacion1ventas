"""
Punto de entrada principal para el procesamiento y exportación de productos.
"""

import argparse
import sys
from typing import List

from constants import DEFAULT_INPUT_FILE
from data_loader import flatten_products, load_json_data
from exporter import export_rejected_csv, export_user_csv
from sorter import sort_products
from ui import (
    display_rejections,
    display_summary,
    print_banner,
    prompt_separator,
    prompt_sort_criterion,
    prompt_sort_order
)
from validator import validate_and_process_data


def parse_arguments() -> argparse.Namespace:
    """Configura y parsea argumentos opcionales por línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Procesa 'productos.json' y genera archivos CSV por usuario."
    )
    parser.add_argument(
        "--file",
        "-f",
        default=DEFAULT_INPUT_FILE,
        help=f"Ruta al archivo JSON de entrada (por defecto: {DEFAULT_INPUT_FILE})"
    )
    parser.add_argument(
        "--separator",
        "-s",
        choices=[",", ";"],
        default=None,
        help="Separador para el archivo CSV (',' o ';'). Si no se especifica, se preguntará interactivamente."
    )
    parser.add_argument(
        "--sort",
        choices=["nombre", "precio", "stock"],
        default=None,
        help="Criterio de ordenamiento. Si no se especifica, se preguntará interactivamente."
    )
    parser.add_argument(
        "--order",
        choices=["asc", "desc"],
        default=None,
        help="Sentido del ordenamiento: 'asc' o 'desc'. Si no se especifica, se preguntará interactivamente."
    )
    return parser.parse_args()


def run() -> None:
    """Función principal que orquesta el flujo de ejecución completo."""
    args = parse_arguments()

    print_banner()

    # 1. Obtener opciones (interactivas si no se pasaron argumentos)
    separator = args.separator if args.separator else prompt_separator()
    sort_criterion = args.sort if args.sort else prompt_sort_criterion()

    if args.order is not None:
        ascending = (args.order == "asc")
    else:
        ascending = prompt_sort_order()

    # 2. Cargar datos del archivo JSON
    input_file = args.file
    try:
        data = load_json_data(input_file)
    except Exception as err:
        print(f"\n[ERROR] No se pudo leer el archivo '{input_file}': {err}")
        sys.exit(1)

    raw_products = data.get("productos", [])

    # 3. Aplanar lista de productos (resolver listas anidadas)
    flat_products = flatten_products(raw_products)

    # 4. Validar y normalizar productos
    valid_products_by_user, rejected_products = validate_and_process_data(data, flat_products)

    # 5. Informar en pantalla los productos rechazados y el motivo
    display_rejections(rejected_products)

    # 6. Exportar un archivo CSV por cada usuario con sus productos ordenados
    exported_user_files: List[str] = []
    for user_id in sorted(valid_products_by_user.keys()):
        user_products = valid_products_by_user[user_id]
        sorted_user_products = sort_products(user_products, sort_criterion, ascending)
        file_path = export_user_csv(user_id, sorted_user_products, delimiter=separator)
        exported_user_files.append(file_path)

    # 7. Exportar productos rechazados (Desafío adicional)
    rejected_file_path = export_rejected_csv(rejected_products, delimiter=separator)

    # 8. Mostrar resumen final
    display_summary(exported_user_files, rejected_file_path)


if __name__ == "__main__":
    run()
