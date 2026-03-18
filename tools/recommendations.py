from typing import List, Dict, Any
import json
import os


DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "products.json")


def _load_products() -> List[Dict[str, Any]]:
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def recommend_products(category: str) -> List[str]:
    """Return simple product name recommendations for a given category or preference."""
    products = _load_products()
    category_lower = (category or "").lower()
    names: List[str] = []
    for p in products:
        product_category = str(p.get("category", "")).lower()
        tags = " ".join(map(str, p.get("tags", []))).lower()
        notes = " ".join(map(str, p.get("notes", []))).lower()
        if category_lower in product_category or category_lower in tags or category_lower in notes:
            names.append(str(p.get("name", "")))
    if not names:
        # Fallback demo recommendations
        return [
            "Nykaa Matte Lipstick",
            "Nykaa Ultra Matte Liquid Lipstick",
            "Nykaa Love Struck Perfume - Vanilla Vibes",
            "Nykaa SkinShield Foundation",
            "Nykaa Curl Power Mascara",
        ]
    return names[:15]

