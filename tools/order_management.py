import json
import os
from typing import Dict, Any, List


ORDERS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "orders.json")


def _load_orders() -> List[Dict[str, Any]]:
    if not os.path.exists(ORDERS_PATH):
        return []
    with open(ORDERS_PATH, encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _save_orders(orders: List[Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(ORDERS_PATH), exist_ok=True)
    with open(ORDERS_PATH, "w", encoding="utf-8") as f:
        json.dump(orders, f, indent=2, ensure_ascii=False)


def create_order(product_id: str, quantity: int) -> Dict[str, Any]:
    """Create a dummy order and persist it to the local JSON file."""
    orders = _load_orders()
    order_id = f"ORD{10000 + len(orders) + 1}"
    order = {
        "order_id": order_id,
        "product_id": product_id,
        "quantity": quantity,
        "status": "confirmed",
    }
    orders.append(order)
    _save_orders(orders)
    return order


def track_order(order_id: str) -> Dict[str, Any]:
    """Return the status of an order. For demo, we simulate a simple lifecycle."""
    orders = _load_orders()
    for order in orders:
        if order.get("order_id") == order_id:
            # Simple demo statuses
            status = order.get("status", "confirmed")
            if status == "confirmed":
                delivery_estimate = "3-5 days"
            elif status == "shipped":
                delivery_estimate = "2 days"
            else:
                delivery_estimate = "N/A"
            return {
                "order_id": order_id,
                "status": status,
                "delivery_estimate": delivery_estimate,
            }
    return {
        "order_id": order_id,
        "status": "not_found",
        "delivery_estimate": "N/A",
    }


def cancel_order(order_id: str) -> Dict[str, Any]:
    """Cancel an order if found."""
    orders = _load_orders()
    for order in orders:
        if order.get("order_id") == order_id:
            if order.get("status") in {"delivered", "cancelled"}:
                return {"order_id": order_id, "status": order.get("status")}
            order["status"] = "cancelled"
            _save_orders(orders)
            return {"order_id": order_id, "status": "cancelled"}

    return {"order_id": order_id, "status": "not_found"}

