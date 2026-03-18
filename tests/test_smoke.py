import json
import os


def test_products_json_is_valid() -> None:
    base_dir = os.path.dirname(os.path.dirname(__file__))
    products_path = os.path.join(base_dir, "data", "products.json")
    with open(products_path, encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) >= 10


def test_search_products_returns_results() -> None:
    from tools.product_search import search_products

    results = search_products("vanilla perfume")
    assert results, "Expected non-empty results for vanilla perfume"


def test_recommend_products_returns_results() -> None:
    from tools.recommendations import recommend_products

    results = recommend_products("vanilla")
    assert results, "Expected non-empty recommendations for vanilla"

