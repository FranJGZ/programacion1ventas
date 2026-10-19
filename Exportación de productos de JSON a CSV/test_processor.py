"""
Suite de pruebas unitarias e integrales para el procesador de productos y CSV.
"""

import csv
import os
import tempfile
import unittest

from constants import (
    DEFAULT_CATEGORY,
    REJECTED_CSV_COLUMNS,
    USER_CSV_COLUMNS
)
from data_loader import flatten_products, load_json_data
from exporter import export_rejected_csv, export_user_csv
from sorter import sort_products
from validator import clean_string, normalize_numeric_fields, validate_and_process_data


class TestDataLoader(unittest.TestCase):
    def test_flatten_products_single_and_nested(self):
        sample = [
            {"id": 1},
            [
                {"id": 2},
                {"id": 3}
            ],
            {"id": 4},
            [
                [
                    {"id": 5}
                ],
                {"id": 6}
            ]
        ]
        flattened = flatten_products(sample)
        self.assertEqual(len(flattened), 6)
        ids = [item["id"] for item in flattened]
        self.assertEqual(ids, [1, 2, 3, 4, 5, 6])


class TestValidator(unittest.TestCase):
    def setUp(self):
        self.mock_data = {
            "usuarios": [
                {"id_usuario": 101, "nombre": "Ana López"},
                {"id_usuario": 202, "nombre": "Carlos Gómez"}
            ]
        }

    def test_clean_string(self):
        self.assertEqual(clean_string("  Notebook básica  "), "Notebook básica")
        self.assertEqual(clean_string("  Multiple   espacios  "), "Multiple espacios")
        self.assertEqual(clean_string(None), "")

    def test_normalize_numeric_fields(self):
        pid, precio, stock = normalize_numeric_fields(1, "25000.50", "15")
        self.assertEqual(pid, 1)
        self.assertEqual(precio, 25000.5)
        self.assertEqual(stock, 15)
        self.assertIsInstance(precio, float)
        self.assertIsInstance(stock, int)

    def test_validation_valid_products(self):
        products = [
            {
                "id": 1,
                "id_usuario": 101,
                "nombre": "  Teclado  ",
                "categoria": "Periféricos",
                "precio": "1000",
                "stock": "5"
            },
            {
                "id": 2,
                "id_usuario": 101,
                "nombre": "Mouse",
                "precio": 500,
                "stock": 10
            }
        ]
        valid_by_user, rejected = validate_and_process_data(self.mock_data, products)
        self.assertEqual(len(rejected), 0)
        self.assertIn(101, valid_by_user)
        self.assertEqual(len(valid_by_user[101]), 2)
        # Check normalization
        p1 = valid_by_user[101][0]
        self.assertEqual(p1["nombre"], "Teclado")
        p2 = valid_by_user[101][1]
        self.assertEqual(p2["categoria"], DEFAULT_CATEGORY)

    def test_validation_rejections(self):
        products = [
            # 1. Missing price (null)
            {"id": 10, "id_usuario": 101, "nombre": "Item A", "precio": None, "stock": 5},
            # 2. Invalid stock (empty string)
            {"id": 11, "id_usuario": 101, "nombre": "Item B", "precio": 100, "stock": ""},
            # 3. Duplicate ID
            {"id": 12, "id_usuario": 101, "nombre": "Item C1", "precio": 100, "stock": 5},
            {"id": 12, "id_usuario": 101, "nombre": "Item C2", "precio": 200, "stock": 10},
            # 4. Unknown user
            {"id": 13, "id_usuario": 999, "nombre": "Item D", "precio": 100, "stock": 5}
        ]
        valid_by_user, rejected = validate_and_process_data(self.mock_data, products)
        self.assertEqual(len(rejected), 4)
        rejected_ids = [r["id"] for r in rejected]
        self.assertIn(10, rejected_ids)
        self.assertIn(11, rejected_ids)
        self.assertIn(12, rejected_ids)
        self.assertIn(13, rejected_ids)


class TestSorter(unittest.TestCase):
    def setUp(self):
        self.products = [
            {"id": 1, "nombre": "Zeta", "precio": 300.0, "stock": 10},
            {"id": 2, "nombre": "Alfa", "precio": 100.0, "stock": 50},
            {"id": 3, "nombre": "Beta", "precio": 200.0, "stock": 5}
        ]

    def test_sort_by_name(self):
        asc = sort_products(self.products, "nombre", ascending=True)
        self.assertEqual([p["nombre"] for p in asc], ["Alfa", "Beta", "Zeta"])

        desc = sort_products(self.products, "nombre", ascending=False)
        self.assertEqual([p["nombre"] for p in desc], ["Zeta", "Beta", "Alfa"])

    def test_sort_by_price(self):
        asc = sort_products(self.products, "precio", ascending=True)
        self.assertEqual([p["precio"] for p in asc], [100.0, 200.0, 300.0])

        desc = sort_products(self.products, "precio", ascending=False)
        self.assertEqual([p["precio"] for p in desc], [300.0, 200.0, 100.0])

    def test_sort_by_stock(self):
        asc = sort_products(self.products, "stock", ascending=True)
        self.assertEqual([p["stock"] for p in asc], [5, 10, 50])

        desc = sort_products(self.products, "stock", ascending=False)
        self.assertEqual([p["stock"] for p in desc], [50, 10, 5])


class TestExporter(unittest.TestCase):
    def test_export_user_csv_columns_and_escaping(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            sample_products = [
                {
                    "id": 5,
                    "nombre": "Auriculares, edición gamer",
                    "categoria": "Sin categoría",
                    "precio": 45000.0,
                    "stock": 10
                }
            ]
            file_path = export_user_csv(101, sample_products, delimiter=",", output_dir=tmpdir)
            self.assertTrue(os.path.exists(file_path))

            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f, delimiter=",")
                rows = list(reader)

            # Check header
            self.assertEqual(rows[0], USER_CSV_COLUMNS)
            # Check row content
            self.assertEqual(rows[1][0], "5")
            self.assertEqual(rows[1][1], "Auriculares, edición gamer")
            self.assertEqual(rows[1][2], "Sin categoría")

    def test_export_rejected_csv(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            rejected = [
                {"id": 7, "nombre": "Soporte", "motivo": "Precio faltante"}
            ]
            file_path = export_rejected_csv(rejected, delimiter=";", output_dir=tmpdir)
            self.assertTrue(os.path.exists(file_path))

            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f, delimiter=";")
                rows = list(reader)

            self.assertEqual(rows[0], REJECTED_CSV_COLUMNS)
            self.assertEqual(rows[1], ["7", "Soporte", "Precio faltante"])


class TestEndToEndWithProductosJson(unittest.TestCase):
    def test_sample_productos_json(self):
        # Aseguramos que productos.json existe en la raíz
        self.assertTrue(os.path.exists("productos.json"))

        data = load_json_data("productos.json")
        flat = flatten_products(data.get("productos", []))
        self.assertEqual(len(flat), 10)

        valid_by_user, rejected = validate_and_process_data(data, flat)

        # 6 válidos (3 para 101, 3 para 202)
        self.assertEqual(len(valid_by_user[101]), 3)
        self.assertEqual(len(valid_by_user[202]), 3)

        # 4 rechazados (7, 8 stock vacío, 8 duplicado, 9 usuario inexistente)
        self.assertEqual(len(rejected), 4)

        rejected_ids = [r["id"] for r in rejected]
        self.assertEqual(rejected_ids, [7, 8, 8, 9])


if __name__ == "__main__":
    unittest.main()
