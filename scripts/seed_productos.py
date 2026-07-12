"""
Puebla el catálogo llamando a la API de productos (POST /api/productos),
que es la única vía para cargar productos en la base de datos.

Requiere que la app esté corriendo.

Uso:
    python scripts/seed_productos.py
    API_BASE_URL=https://mi-app.onrender.com python scripts/seed_productos.py
"""
import json
import os
import sys

import requests

RUTA_JSON = os.path.join(os.path.dirname(__file__), "..", "data", "productos.json")
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:5000").rstrip("/")


def main():
    with open(RUTA_JSON, encoding="utf-8") as f:
        productos = json.load(f)

    creados, fallidos = 0, 0
    for p in productos:
        payload = {
            "nombre": p["nombre"],
            "descripcion": p["descripcion"],
            "categoria": p["categoria"],
            "precio": p["precio"],
            "stock": p["stock"],
            "imagen": p["imagen"],
            "estado": "Agotado" if p["stock"] == 0 else "Activo",
        }
        resp = requests.post(f"{API_BASE_URL}/api/productos", json=payload, timeout=10)
        if resp.status_code == 201:
            creados += 1
            print(f"OK    {p['nombre']}")
        else:
            fallidos += 1
            print(f"ERROR {p['nombre']}: {resp.status_code} {resp.text}")

    print(f"\n{creados} productos creados, {fallidos} fallidos.")
    if fallidos:
        sys.exit(1)


if __name__ == "__main__":
    main()
