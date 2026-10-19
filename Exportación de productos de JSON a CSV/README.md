# Procesador y Exportador de Productos JSON a CSV

Sistema modular en Python diseñado para procesar archivos de datos de productos en formato JSON (`productos.json`), aplanar estructuras anidadas, validar la integridad referencial y de tipos, depurar registros defectuosos y exportar archivos CSV independientes y ordenados por cada usuario administrador, además de generar un reporte de productos rechazados.

---

## 📁 Arquitectura Modular del Proyecto

La aplicación fue desarrollada siguiendo el principio de responsabilidad única (Single Responsibility Principle), dividida en módulos independientes:

```text
├── productos.json           # Archivo de entrada con usuarios y productos
├── main.py                  # Orquestador principal y punto de entrada (CLI/interactivo)
├── constants.py             # Constantes globales, columnas y rutas
├── data_loader.py           # Lectura de JSON y aplanamiento recursivo de listas
├── validator.py             # Limpieza, normalización y reglas de validación
├── sorter.py                # Algoritmos de ordenamiento parametrizados
├── exporter.py              # Generación de archivos CSV mediante csv.DictWriter
├── ui.py                    # Interfaz de usuario de consola (menús y tablas de reporte)
├── test_processor.py        # Suite de pruebas unitarias e integrales (unittest)
├── README.md                # Documentación del proyecto, respuestas y guía de Git
└── .gitignore               # Exclusiones de control de versiones
```

### Descripción de cada módulo:
* **`constants.py`**: Centraliza las definiciones del sistema: orden estricto de columnas para los CSV de usuarios (`id, nombre, categoria, precio, stock`) y para el archivo de rechazados (`id, nombre, motivo`), nombres de archivos y valores predeterminados.
* **`data_loader.py`**: Maneja la apertura y decodificación de `productos.json` en UTF-8 y proporciona la función `flatten_products`, que recorre y aplana recursivamente sublistas anidadas de productos a cualquier nivel de profundidad.
* **`validator.py`**: Contiene la lógica de negocio para:
  * Eliminar espacios sobrantes en textos (`strip` y colapso de espacios múltiples).
  * Validar tipos de datos numéricos y convertirlos (`int` para `id` y `stock`, `float` para `precio`).
  * Asignar `"Sin categoría"` a productos sin categoría o con categoría nula/vacía.
  * Detectar duplicados de IDs y rechazar relaciones con usuarios inexistentes.
* **`sorter.py`**: Proporciona ordenamiento flexible por `nombre` (alfabético no sensible a mayúsculas), `precio` (numérico) o `stock` (numérico), con opción ascendente o descendente.
* **`exporter.py`**: Encapsula el uso de `csv.DictWriter` para escribir de forma segura los CSV de cada usuario (`productos_101.csv`, `productos_202.csv`) y de productos rechazados (`productos_rechazados.csv`).
* **`ui.py`**: Ofrece menús interactivos guiados con validación de entradas de usuario y presentación en consola de los productos rechazados con su motivo.

---

## 🚀 Requisitos y Ejecución

### Prerrequisitos
* Python 3.8 o superior (no requiere librerías externas; utiliza únicamente la biblioteca estándar).

### Ejecución Interactiva (Recomendada)
Para iniciar el programa con menús guiados interactivos:
```bash
python main.py
```
El sistema solicitará:
1. El separador a utilizar:
   * `1` o `,` para Coma.
   * `2` o `;` para Punto y coma.
2. El criterio de ordenamiento:
   * `1` para Nombre.
   * `2` para Precio.
   * `3` para Stock.
3. El sentido del orden:
   * `1` para Ascendente.
   * `2` para Descendente.

### Ejecución Parametrizada por Línea de Comandos (CLI)
También es posible pasar argumentos para automatizaciones:
```bash
# Ejemplo: separador coma, ordenado por precio de forma ascendente
python main.py --separator "," --sort precio --order asc

# Ejemplo: separador punto y coma, ordenado por stock descendente
python main.py --separator ";" --sort stock --order desc
```

### Ejecutar Pruebas Automatizadas
Para ejecutar la suite completa de pruebas unitarias e integrales:
```bash
python -m unittest test_processor.py -v
```

---

## 📊 Archivos Generados

Al procesar `productos.json`:
1. **`productos_101.csv`**: Productos válidos administrados por Ana López (ID 101), con columnas:
   ```text
   id, nombre, categoria, precio, stock
   ```
2. **`productos_202.csv`**: Productos válidos administrados por Carlos Gómez (ID 202), con las mismas columnas.
3. **`productos_rechazados.csv`**: Registro de productos no exportables con sus motivos de rechazo:
   ```text
   id, nombre, motivo
   ```

---

## ❓ Preguntas para Analizar y Respuestas Detalladas

### 1. ¿Por qué fue necesario transformar algunos datos antes de escribirlos en el CSV?
En el archivo `productos.json` de origen, los datos presentaban inconsistencias de tipo y formato:
* **Tipos de datos numéricos como cadenas**: Valores como `"precio": "25000.50"` o `"stock": "15"` venían representados como `string`. Si no se transformaban a tipos numéricos (`float` e `int`), cualquier ordenamiento posterior operaría de forma lexicográfica (alfabética). En orden alfabético, `"180000" < "25000.50"` y `"15" < "4"`, lo cual arroja resultados matemáticamente incorrectos.
* **Validación de integridad**: Al intentar convertir explícitamente a `float` o `int`, el programa puede atrapar errores como valores vacíos (`""`), caracteres no numéricos o cantidades negativas.
* **Espacios sobrantes**: Cadenas como `"  Notebook básica  "` contenían espacios que contaminan la presentación y alteran el ordenamiento.
* **Valores nulos o ausentes**: Productos sin categoría (`null` o clave inexistente) debían normalizarse con el valor por defecto `"Sin categoría"` para garantizar uniformidad en las columnas.

### 2. ¿Qué problema presentaba la estructura de la lista de productos?
La lista de productos contenía **listas anidadas** (sublistas de diccionarios dentro de la lista principal). Una lectura ingenua con un bucle simple (`for producto in productos:`) fallaba inmediatamente al intentar acceder a `producto['id']` sobre un elemento que era una lista (`TypeError: list indices must be integers or slices, not str`).
Para solucionar esto, se implementó una función recursiva de aplanamiento (`flatten_products`) que recorre cualquier nivel de anidamiento y devuelve una lista lineal limpia con todos los diccionarios individuales listos para su validación.

### 3. ¿Qué diferencia produce utilizar coma o punto y coma como separador?
* **Coma (`,`)**: Es el estándar tradicional para archivos CSV (RFC 4180). Es ampliamente adoptado por lenguajes de programación, librerías de ciencia de datos (Pandas, R) y sistemas con configuración regional en inglés (donde el punto es el separador decimal).
* **Punto y coma (`;`)**: Es el estándar predilecto en países hispanohablantes y en Microsoft Excel con configuración regional europea o latinoamericana. En estas regiones, la coma se utiliza como separador de decimales (ejemplo: `25000,50`). Si se abre un archivo delimitado por comas en un Excel en español, el programa interpreta las comas de los números como delimitadores de columnas, corrompiendo la tabla. Utilizar `;` permite una apertura limpia y directa con doble clic en Excel en español.

### 4. ¿Qué sucede cuando el nombre de un producto contiene una coma?
En el caso del producto `"Auriculares, edición gamer"`:
* **Si el separador del CSV es la coma (`,`)**: Existe una colisión directa entre el delimitador de campos y el contenido del texto. Si no se tomaran recaudos, un lector de CSV interpretaría `"Auriculares"` como el campo `nombre` y `" edición gamer"` como el campo `categoria`, desalineando todas las columnas siguientes. Por especificación RFC 4180, el valor debe ser envuelto entre comillas dobles: `"Auriculares, edición gamer"`.
* **Si el separador del CSV es el punto y coma (`;`)**: La coma interna no colisiona con el separador de columnas, por lo que el texto puede escribirse directamente sin necesidad de comillas obligatorias.

### 5. ¿Por qué se utiliza `csv.DictWriter` en lugar de construir las filas manualmente?
* **Manejo automático del entrecomillado y escape (RFC 4180)**: Construir filas manualmente concatenando cadenas (`f"{id},{nombre},{categoria}..."`) obliga al programador a reinventar la lógica para detectar si un campo contiene comas, saltos de línea o comillas, y escapar cada uno manualmente. `csv.DictWriter` gestiona esto de forma automática, eficiente y estandarizada.
* **Mapeo desacoplado por nombres de campos (`fieldnames`)**: Al trabajar con diccionarios, `DictWriter` asocia cada dato a su cabecera independientemente del orden en el que figuren las claves dentro del diccionario Python.
* **Prevención de corrupciones por cambios en el esquema**: Si se agrega, renombra o reordena un campo, `DictWriter` mantiene la coherencia entre cabecera y filas sin peligro de desfasar columnas.
* **Configurabilidad**: Permite cambiar el delimitador (`delimiter=','` o `delimiter=';'`) en un solo parámetro sin tocar una sola línea de lógica de datos.

### 6. ¿Cómo se decidió el orden de las columnas del CSV?
El orden fue determinado por el **Requerimiento 9** de la especificación técnica:
```text
id, nombre, categoria, precio, stock
```
Desde las buenas prácticas de diseño de información y bases de datos:
1. **`id`**: Clave primaria identificadora única de la fila.
2. **`nombre`**: Descriptor principal y legible por humanos del registro.
3. **`categoria`**: Atributo cualitativo de agrupación.
4. **`precio`**: Atributo cuantitativo económico.
5. **`stock`**: Atributo cuantitativo de inventario.


