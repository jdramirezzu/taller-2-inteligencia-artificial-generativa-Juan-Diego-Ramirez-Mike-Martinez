"""Consulta de pedidos por número de seguimiento (viene del Taller 1).

Los pedidos NO se guardan en la base vectorial: se buscan por su número exacto (ECM-XXXX).
Para un dato exacto, una búsqueda por clave es más confiable que una búsqueda por similitud.
"""
import json
import re
from typing import Optional

import config

PATRON_TRACKING = re.compile(r"ECM-\d{4}", re.IGNORECASE)


def cargar_pedidos() -> list[dict]:
    with open(config.RUTA_PEDIDOS_JSON, encoding="utf-8") as f:
        return json.load(f)


def buscar_pedido(tracking_number: str) -> Optional[dict]:
    tracking_number = tracking_number.strip().upper()
    for pedido in cargar_pedidos():
        if pedido["tracking_number"].upper() == tracking_number:
            return pedido
    return None


def detectar_tracking(mensaje: str) -> Optional[str]:
    """Busca un número de seguimiento escrito dentro del mensaje del cliente."""
    encontrado = PATRON_TRACKING.search(mensaje)
    return encontrado.group(0).upper() if encontrado else None


def pedido_a_contexto(tracking_number: Optional[str]) -> str:
    """Devuelve los datos del pedido como texto para ponerlos en el prompt."""
    if tracking_number is None:
        return "El cliente no dio un número de seguimiento."
    pedido = buscar_pedido(tracking_number)
    if pedido is None:
        return f"No se encontró ningún pedido con el número de seguimiento {tracking_number}."
    campos = [
        f"Número de seguimiento: {pedido['tracking_number']}",
        f"Cliente: {pedido['customer_name']}",
        f"Producto: {pedido['product']} (categoría: {pedido['product_category']})",
        f"¿Es devolvible?: {'sí' if pedido['returnable'] else 'no'}",
        f"Estado: {pedido['status']}",
        f"Fecha de pedido: {pedido['order_date']}",
        f"Entrega estimada: {pedido['estimated_delivery']}",
        f"Entrega real: {pedido['actual_delivery'] or 'todavía no entregado'}",
        f"Ciudad de entrega: {pedido['delivery_city']}",
    ]
    if pedido.get("notes"):
        campos.append(f"Notas internas: {pedido['notes']}")
    return "\n".join(campos)
