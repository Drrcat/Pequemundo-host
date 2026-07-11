from flask import Blueprint, request, jsonify
from services.sabor_latino_service import obtener_productos, normalizar_producto

api_bp = Blueprint('api', __name__)

# Nota: /api/productos, /api/productos/<id> y /api/categorias los sirve ahora
# apis/productos_api.py (productos_api_bp), conectado directamente a la BD.


@api_bp.route('/api/socios/sabor-latino')
def api_sabor_latino():
    categoria = request.args.get('categoria', '').strip()
    try:
        productos = obtener_productos(categoria or None)
        return jsonify([normalizar_producto(p) for p in productos])
    except Exception as e:
        return jsonify({"error": "No se pudo conectar con el socio", "detalle": str(e)}), 503


@api_bp.route('/api/socios/sabor-latino/<string:sku>')
def api_sabor_latino_producto(sku):
    try:
        productos = obtener_productos()
        producto = next((p for p in productos if p["sku"] == sku), None)
        if not producto:
            return jsonify({"error": f"Producto {sku} no encontrado"}), 404
        return jsonify(normalizar_producto(producto))
    except Exception as e:
        return jsonify({"error": "No se pudo conectar con el socio", "detalle": str(e)}), 503