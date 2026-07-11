import requests
import urllib3
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from extensions import db
from models import Producto, Pedido, Usuario
from decorators import requiere_admin

admin_bp = Blueprint('admin', __name__)

# Llamadas internas al self-signed cert de "flask run --cert=adhoc" en dev local.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _productos_api(method, path, **kwargs):
    """Llama a la API de productos (apis/productos_api.py), que es quien escribe en la BD."""
    url = f"{request.host_url.rstrip('/')}{path}"
    kwargs.setdefault('timeout', 10)
    if request.is_secure:
        kwargs.setdefault('verify', False)
    return requests.request(method, url, **kwargs)


def _form_a_payload(form):
    return {
        'nombre': form['nombre'],
        'descripcion': form['descripcion'],
        'imagen': form['imagen'],
        'categoria': form['categoria'],
        'precio': form['precio'],
        'stock': form['stock'],
        'estado': form['estado'],
    }


@admin_bp.route('/admin')
@requiere_admin
def dashboard():
    productos = Producto.query.all()
    pedidos = Pedido.query.all()
    usuarios = Usuario.query.all()
    return render_template('dashboard.html', productos=productos, pedidos=pedidos, usuarios=usuarios)


@admin_bp.route('/admin/panel')
@requiere_admin
def admin_dashboard():
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/admin/productos')
@requiere_admin
def productos():
    productos = Producto.query.all()
    return render_template('productos.html', productos=productos)


@admin_bp.route('/admin/agregar', methods=['GET', 'POST'])
@requiere_admin
def agregar_producto():
    if request.method == 'POST':
        try:
            resp = _productos_api('POST', '/api/productos', json=_form_a_payload(request.form))
        except requests.RequestException as e:
            flash(f'No se pudo conectar con la API de productos: {e}', 'danger')
            return render_template('agregar_producto.html')
        if resp.status_code == 201:
            flash('Producto agregado correctamente.', 'success')
            return redirect(url_for('admin.productos'))
        flash(f"Error al agregar producto: {resp.json().get('error', resp.text)}", 'danger')
        return render_template('agregar_producto.html')
    return render_template('agregar_producto.html')


@admin_bp.route('/admin/editar/<int:id>', methods=['GET', 'POST'])
@requiere_admin
def editar_producto(id):
    try:
        get_resp = _productos_api('GET', f'/api/productos/{id}')
    except requests.RequestException as e:
        flash(f'No se pudo conectar con la API de productos: {e}', 'danger')
        return redirect(url_for('admin.productos'))
    if get_resp.status_code == 404:
        abort(404)
    if get_resp.status_code != 200:
        flash('No se pudo obtener el producto.', 'danger')
        return redirect(url_for('admin.productos'))
    producto = get_resp.json()

    if request.method == 'POST':
        payload = _form_a_payload(request.form)
        put_resp = _productos_api('PUT', f'/api/productos/{id}', json=payload)
        if put_resp.status_code == 200:
            flash('Producto actualizado.', 'success')
            return redirect(url_for('admin.productos'))
        flash(f"Error al actualizar producto: {put_resp.json().get('error', put_resp.text)}", 'danger')
        producto = {**producto, **payload}

    return render_template('editar_producto.html', producto=producto)


@admin_bp.route('/admin/eliminar/<int:id>', methods=['POST'])
@requiere_admin
def eliminar_producto(id):
    try:
        resp = _productos_api('DELETE', f'/api/productos/{id}')
    except requests.RequestException as e:
        flash(f'No se pudo conectar con la API de productos: {e}', 'danger')
        return redirect(url_for('admin.productos'))
    if resp.status_code == 404:
        abort(404)
    if resp.status_code != 200:
        flash(f"Error al eliminar producto: {resp.json().get('error', resp.text)}", 'danger')
        return redirect(url_for('admin.productos'))
    flash('Producto eliminado.', 'success')
    return redirect(url_for('admin.productos'))


@admin_bp.route('/admin/pedidos')
@requiere_admin
def pedidos():
    pedidos = Pedido.query.all()
    return render_template('pedidos.html', pedidos=pedidos)


@admin_bp.route('/admin/usuarios')
@requiere_admin
def usuarios():
    usuarios = Usuario.query.all()
    return render_template('usuarios.html', usuarios=usuarios)


@admin_bp.route('/admin/actualizar_rol/<int:id>', methods=['POST'])
@requiere_admin
def actualizar_rol(id):
    usuario = db.session.get(Usuario, id)
    if not usuario:
        abort(404)
    usuario.rol = request.form['rol']
    db.session.commit()
    flash('Rol actualizado.', 'success')
    return redirect(url_for('admin.usuarios'))
