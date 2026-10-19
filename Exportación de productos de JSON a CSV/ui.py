"""
Módulo de interfaz de usuario por consola (menús interactivos y reportes).
"""

from typing import Any, Dict, List


def print_banner() -> None:
    """Muestra el encabezado del programa."""
    print("=" * 70)
    print("     SISTEMA DE PROCESAMIENTO Y EXPORTACIÓN DE PRODUCTOS A CSV     ")
    print("=" * 70)


def prompt_separator() -> str:
    """
    Solicita al usuario el separador deseado para los archivos CSV.

    Opciones:
    - Coma (,)
    - Punto y coma (;)

    Returns:
        ',' o ';'
    """
    while True:
        print("\nSeleccione el separador para los archivos CSV:")
        print("  [1] Coma ( , )")
        print("  [2] Punto y coma ( ; )")
        choice = input("Ingrese una opción (1 o 2, o el carácter directamente): ").strip()

        if choice in ("1", ","):
            return ","
        elif choice in ("2", ";"):
            return ";"
        else:
            print(">> Opción no válida. Por favor ingrese 1 para coma o 2 para punto y coma.")


def prompt_sort_criterion() -> str:
    """
    Solicita al usuario el criterio de ordenamiento de los productos.

    Opciones:
    - nombre
    - precio
    - stock

    Returns:
        'nombre', 'precio' o 'stock'
    """
    while True:
        print("\nSeleccione el criterio para ordenar los productos:")
        print("  [1] Por nombre")
        print("  [2] Por precio")
        print("  [3] Por stock")
        choice = input("Ingrese una opción (1, 2 o 3): ").strip()

        if choice in ("1", "nombre"):
            return "nombre"
        elif choice in ("2", "precio"):
            return "precio"
        elif choice in ("3", "stock"):
            return "stock"
        else:
            print(">> Opción no válida. Por favor elija 1, 2 o 3.")


def prompt_sort_order() -> bool:
    """
    Solicita al usuario el sentido del ordenamiento.

    Opciones:
    - Ascendente
    - Descendente

    Returns:
        True si es ascendente, False si es descendente.
    """
    while True:
        print("\nSeleccione el sentido del ordenamiento:")
        print("  [1] Ascendente (A-Z, menor a mayor)")
        print("  [2] Descendente (Z-A, mayor a menor)")
        choice = input("Ingrese una opción (1 o 2): ").strip()

        if choice in ("1", "asc", "ascendente"):
            return True
        elif choice in ("2", "desc", "descendente"):
            return False
        else:
            print(">> Opción no válida. Por favor elija 1 para ascendente o 2 para descendente.")


def display_rejections(rejected_products: List[Dict[str, Any]]) -> None:
    """
    Informa en pantalla los productos que fueron rechazados y el motivo.
    """
    print("\n" + "-" * 70)
    print("                    PRODUCTOS RECHAZADOS                          ")
    print("-" * 70)

    if not rejected_products:
        print("No se registraron productos rechazados. Todos los datos son válidos.")
        return

    print(f"Total de productos rechazados: {len(rejected_products)}\n")
    for idx, item in enumerate(rejected_products, start=1):
        pid = item.get("id", "N/A")
        nombre = item.get("nombre", "Sin nombre")
        motivo = item.get("motivo", "No especificado")
        print(f"  {idx}. [ID: {pid}] \"{nombre}\"")
        print(f"     -> Motivo: {motivo}")

    print("-" * 70)


def display_summary(exported_files: List[str], rejected_file: str) -> None:
    """
    Muestra el resumen final de la exportación exitosa.
    """
    print("\n" + "=" * 70)
    print("                      PROCESO COMPLETADO                          ")
    print("=" * 70)
    print("Archivos generados exitosamente:")
    for path in exported_files:
        print(f"  [+] {path}")
    print(f"  [!] {rejected_file} (Productos rechazados)")
    print("=" * 70 + "\n")
