import json
import os
from typing import List, Dict, Any


DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "products.json"
)


def search_products(query: str) -> List[Dict[str, Any]]:
    """Search Nykaa-style products by free-text query.

    The query should capture the shopper's intent as much as possible,
    for example: "warm vanilla perfume under 2000 for date night",
    "matte lipstick for office, pink nude", or "skincare kit for oily skin".

    The agent is expected to first clarify:
      - product type (lipstick, foundation, perfume, skincare kit, etc.)
      - key preferences (finish, skin type, scent note like vanilla, budget)
      - occasion (everyday, office, party, date night)

    Then pass a short, focused query string that includes those details.
    This tool returns up to 15 of the best-matching products.
    """
    if not query:
        return []

    with open(DATA_PATH, encoding="utf-8") as f:
        products = json.load(f)

    q = query.lower().strip()
    tokens = [t for t in (w.strip(" ,.!?;:/()[]{}'\"").lower() for w in q.split()) if len(t) >= 3]

    scored: List[tuple[int, Dict[str, Any]]] = []
    for p in products:
        name = str(p.get("name", "")).lower()
        category = str(p.get("category", "")).lower()
        tags = " ".join(map(str, p.get("tags", []))).lower()
        notes = " ".join(map(str, p.get("notes", []))).lower()
        haystack = f"{name} {category} {tags} {notes}"

        # Strong match if full query is a substring (works for short queries like "vanilla").
        score = 10 if q and q in haystack else 0

        # Otherwise score by token overlaps for longer, natural-language queries.
        if tokens:
            score += sum(1 for t in tokens if t in haystack)

        if score > 0:
            scored.append((score, p))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:15]]

