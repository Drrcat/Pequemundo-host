import os
import mercadopago

MP_ACCESS_TOKEN = os.environ.get(
    'MP_ACCESS_TOKEN',
    'APP_USR-2602588492542868-052513-1b2fa70861fd23856b1622fbdb502567-3250900679'
)
sdk = mercadopago.SDK(MP_ACCESS_TOKEN)


def crear_preferencia(items_list, cliente_nombre, cliente_email, pedido_id, base_url):
    mp_items = [{
        "id": str(i['id']),
        "title": i['nombre'],
        "quantity": int(i['cantidad']),
        "unit_price": int(i['precio']),
        "currency_id": "CLP"
    } for i in items_list]

    preference_data = {
        "items": mp_items,
        "payer": {
            "name": cliente_nombre,
            "email": cliente_email or ""
        },
        "back_urls": {
            "success": f"{base_url}/mp/success",
            "failure": f"{base_url}/mp/failure",
            "pending": f"{base_url}/mp/pending",
        },
        "auto_return": "approved",
        "external_reference": str(pedido_id),
    }

    response = sdk.preference().create(preference_data)
    return response.get("response", {})


def obtener_pago(payment_id):
    response = sdk.payment().get(payment_id)
    return response.get("response", {})
