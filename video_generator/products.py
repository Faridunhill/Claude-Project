import json
from pathlib import Path
from typing import Any

from . import config


Product = dict[str, Any]


def load_all_products() -> list[Product]:
    products = []
    for dept, filename in config.DEPT_FILES.items():
        path = Path(config.DATA_DIR) / filename
        if not path.exists():
            continue
        try:
            items = json.loads(path.read_text())
            products.extend(items)
        except (json.JSONDecodeError, OSError):
            continue
    return products


def load_department(department: str) -> list[Product]:
    if department not in config.DEPT_FILES:
        raise ValueError(
            f"Unknown department: {department!r}. "
            f"Valid options: {', '.join(config.DEPT_FILES)}"
        )
    path = Path(config.DATA_DIR) / config.DEPT_FILES[department]
    if not path.exists():
        raise FileNotFoundError(f"Product file not found: {path}")
    return json.loads(path.read_text())


def find_product_by_id(product_id: str, products: list[Product]) -> Product | None:
    for p in products:
        if p.get("id") == product_id:
            return p
    return None


def find_product_by_slug(slug: str, products: list[Product]) -> Product | None:
    for p in products:
        if p.get("slug") == slug:
            return p
    return None


def find_product_by_name(name: str, products: list[Product]) -> Product | None:
    name_lower = name.lower()
    for p in products:
        if name_lower in p.get("name", "").lower():
            return p
    return None


def select_single(query: str) -> Product:
    """Find a product by id, slug, or name substring across all departments."""
    all_products = load_all_products()

    found = (
        find_product_by_id(query, all_products)
        or find_product_by_slug(query, all_products)
        or find_product_by_name(query, all_products)
    )

    if not found:
        raise ValueError(
            f"No product found matching {query!r}. "
            "Try the product ID (e.g. pipe-001), slug, or part of the name."
        )
    return found


def select_featured(department: str, max_products: int = 4) -> list[Product]:
    """Return up to max_products featured, in-stock items from a department."""
    items = load_department(department)
    featured = [p for p in items if p.get("featured") and p.get("inStock", True)]
    if not featured:
        featured = [p for p in items if p.get("inStock", True)]
    return featured[:max_products]


def format_product_for_prompt(product: Product) -> dict:
    """Strip fields Claude doesn't need; format price as a string."""
    keep = {
        "name": product.get("name"),
        "brand": product.get("brand"),
        "price": f"${product['price']:.2f}" if product.get("price") else None,
        "original_price": (
            f"${product['originalPrice']:.2f}" if product.get("originalPrice") else None
        ),
        "department": product.get("department"),
        "category": product.get("category"),
        "description": product.get("description"),
        "rating": product.get("rating"),
        "tags": product.get("tags"),
    }
    # Department-specific fields
    for field in ("specs", "vitola", "size", "origin", "wrapper", "contents"):
        if product.get(field):
            keep[field] = product[field]

    return {k: v for k, v in keep.items() if v is not None}
