"""
Constantes globales para el procesador de productos y exportador CSV.
"""

from typing import List

# Nombres de archivos predeterminados
DEFAULT_INPUT_FILE = "productos.json"
REJECTED_CSV_FILENAME = "productos_rechazados.csv"
USER_CSV_TEMPLATE = "productos_{user_id}.csv"

# Definición y orden estricto de columnas para los archivos CSV
USER_CSV_COLUMNS: List[str] = [
    "id",
    "nombre",
    "categoria",
    "precio",
    "stock"
]

REJECTED_CSV_COLUMNS: List[str] = [
    "id",
    "nombre",
    "motivo"
]

# Valor por defecto cuando un producto no tiene categoría especificada
DEFAULT_CATEGORY = "Sin categoría"

# Separadores permitidos
ALLOWED_SEPARATORS = {
    "1": ",",
    "2": ";",
    ",": ",",
    ";": ";"
}

# Criterios de ordenamiento permitidos
SORT_CRITERIA = {
    "1": "nombre",
    "2": "precio",
    "3": "stock",
    "nombre": "nombre",
    "precio": "precio",
    "stock": "stock"
}
