from flask import Blueprint, jsonify, request
from database.conexion import get_connection, get_cursor

# ── Blueprint (mismo patrón que apis/pedidos_api.py) ────────────────────────
productos_api_bp = Blueprint("productos_api", __name__)

CAMPOS_EDITABLES = ["nombre", "descripcion", "categoria", "precio", "stock", "imagen", "estado"]
CAMPOS_REQUERIDOS = ["nombre", "descripcion", "categoria", "precio", "stock", "imagen"]


def _serializar(p):
    return {
        "id": p["id_producto"],
        "nombre": p["nombre"],
        "descripcion": p["descripcion"],
        "imagen": p["imagen"],
        "categoria": p["categoria"],
        "precio": p["precio"],
        "stock": p["stock"],
        "estado": p["estado"],
    }


def _validar_numeros(body):
    try:
        if "precio" in body:
            body["precio"] = float(body["precio"])
        if "stock" in body:
            body["stock"] = int(body["stock"])
    except (TypeError, ValueError):
        return "precio debe ser numérico y stock debe ser un entero"
    return None


# ── GET /api/productos ───────────────────────────────────────────────────────
@productos_api_bp.get("/api/productos")
def listar_productos():
    categoria = request.args.get("categoria", "").strip()
    try:
        conn = get_connection()
        cursor = get_cursor(conn)
        if categoria:
            cursor.execute(
                "SELECT * FROM producto WHERE categoria = %s AND estado = 'Activo' ORDER BY id_producto",
                (categoria,),
            )
        else:
            cursor.execute("SELECT * FROM producto WHERE estado = 'Activo' ORDER BY id_producto")
        productos = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify([_serializar(p) for p in productos])
    except Exception as e:
        return jsonify({"error": "Error de base de datos", "detalle": str(e)}), 500


# ── GET /api/productos/<id> ──────────────────────────────────────────────────
@productos_api_bp.get("/api/productos/<int:id>")
def obtener_producto(id):
    try:
        conn = get_connection()
        cursor = get_cursor(conn)
        cursor.execute("SELECT * FROM producto WHERE id_producto = %s", (id,))
        producto = cursor.fetchone()
        cursor.close()
        conn.close()
        if producto is None:
            return jsonify({"error": f"Producto #{id} no encontrado"}), 404
        return jsonify(_serializar(producto))
    except Exception as e:
        return jsonify({"error": "Error de base de datos", "detalle": str(e)}), 500


# ── GET /api/categorias ───────────────────────────────────────────────────────
@productos_api_bp.get("/api/categorias")
def listar_categorias():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT DISTINCT categoria FROM producto WHERE estado = 'Activo' ORDER BY categoria"
        )
        categorias = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return jsonify(categorias)
    except Exception as e:
        return jsonify({"error": "Error de base de datos", "detalle": str(e)}), 500


# ── POST /api/productos ───────────────────────────────────────────────────────
@productos_api_bp.post("/api/productos")
def crear_producto():
    """Crea un producto nuevo. Body JSON con: nombre, descripcion, categoria, precio, stock, imagen, estado (opcional)."""
    body = request.get_json(silent=True) or {}
    faltantes = [c for c in CAMPOS_REQUERIDOS if not str(body.get(c, "")).strip()]
    if faltantes:
        return jsonify({"error": f"Faltan campos requeridos: {', '.join(faltantes)}"}), 400

    error = _validar_numeros(body)
    if error:
        return jsonify({"error": error}), 400

    try:
        conn = get_connection()
        cursor = get_cursor(conn)
        cursor.execute(
            """INSERT INTO producto (nombre, descripcion, categoria, precio, stock, imagen, estado)
               VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING *""",
            (
                body["nombre"], body["descripcion"], body["categoria"],
                body["precio"], body["stock"], body["imagen"],
                body.get("estado") or "Activo",
            ),
        )
        nuevo = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify(_serializar(nuevo)), 201
    except Exception as e:
        return jsonify({"error": "Error de base de datos", "detalle": str(e)}), 500


# ── PUT/PATCH /api/productos/<id> ────────────────────────────────────────────
@productos_api_bp.route("/api/productos/<int:id>", methods=["PUT", "PATCH"])
def actualizar_producto(id):
    """Actualiza uno o más campos de un producto existente."""
    body = request.get_json(silent=True) or {}
    campos = [c for c in CAMPOS_EDITABLES if c in body]
    if not campos:
        return jsonify({"error": "No se enviaron campos válidos para actualizar"}), 400

    error = _validar_numeros(body)
    if error:
        return jsonify({"error": error}), 400

    try:
        conn = get_connection()
        cursor = get_cursor(conn)
        cursor.execute("SELECT id_producto FROM producto WHERE id_producto = %s", (id,))
        if cursor.fetchone() is None:
            cursor.close()
            conn.close()
            return jsonify({"error": f"Producto #{id} no encontrado"}), 404

        set_clause = ", ".join(f"{c} = %s" for c in campos)
        valores = [body[c] for c in campos] + [id]
        cursor.execute(
            f"UPDATE producto SET {set_clause} WHERE id_producto = %s RETURNING *",
            valores,
        )
        actualizado = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify(_serializar(actualizado)), 200
    except Exception as e:
        return jsonify({"error": "Error de base de datos", "detalle": str(e)}), 500


# ── DELETE /api/productos/<id> ───────────────────────────────────────────────
@productos_api_bp.delete("/api/productos/<int:id>")
def eliminar_producto(id):
    try:
        conn = get_connection()
        cursor = get_cursor(conn)
        cursor.execute("DELETE FROM producto WHERE id_producto = %s RETURNING id_producto", (id,))
        borrado = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        if borrado is None:
            return jsonify({"error": f"Producto #{id} no encontrado"}), 404
        return jsonify({"mensaje": f"Producto #{id} eliminado"}), 200
    except Exception as e:
        return jsonify({"error": "Error de base de datos", "detalle": str(e)}), 500
