import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests

from utils.logger import get_logger

logger = get_logger(__name__)

PRODUCT_URL_RE = re.compile(r"<loc>(https://[^<]+/productos/[^<]+/)</loc>")
LS_PRODUCT_NAME_RE = re.compile(r"LS\.product\s*=\s*\{.*?name\s*:\s*'((?:[^'\\]|\\.)*)'", re.S)
LS_PRODUCT_TAGS_RE = re.compile(r"LS\.product\s*=\s*\{.*?tags\s*:\s*\[(.*?)\]", re.S)
LS_VARIANTS_RE = re.compile(r"LS\.variants\s*=\s*(\[.*?\]);", re.S)
TAG_ITEM_RE = re.compile(r"'((?:[^'\\]|\\.)*)'")


def _decode_js_string(raw: str) -> str:
    return raw.encode().decode("unicode_escape")


def get_product_urls(store_url: str) -> list[str]:
    resp = requests.get(f"{store_url.rstrip('/')}/sitemap.xml", headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
    resp.raise_for_status()
    return sorted(set(PRODUCT_URL_RE.findall(resp.text)))


def scrape_product(url: str) -> dict | None:
    """Lee LS.product / LS.variants, los mismos objetos JS que usa el storefront
    de Tiendanube para renderizar precio y stock real (no hay endpoint público
    tipo /products.json en Tiendanube)."""
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
    if resp.status_code != 200:
        logger.warning(f"No se pudo leer {url} (HTTP {resp.status_code})")
        return None
    html = resp.text

    variants_match = LS_VARIANTS_RE.search(html)
    if not variants_match:
        logger.warning(f"Sin LS.variants en {url} - se omite (probablemente gift card u otro tipo especial)")
        return None
    variants = json.loads(variants_match.group(1))

    name_match = LS_PRODUCT_NAME_RE.search(html)
    name = _decode_js_string(name_match.group(1)) if name_match else None

    tags_match = LS_PRODUCT_TAGS_RE.search(html)
    tags = [_decode_js_string(t) for t in TAG_ITEM_RE.findall(tags_match.group(1))] if tags_match else []

    available_variants = [v for v in variants if v.get("available")]
    prices = [v["price_number"] for v in variants if v.get("price_number") is not None]
    compare_prices = [v.get("compare_at_price_number") for v in variants if v.get("compare_at_price_number")]
    on_sale = any(
        v.get("compare_at_price_number") and v.get("price_number") and v["compare_at_price_number"] > v["price_number"]
        for v in variants
    )
    image_url = variants[0]["image_url"] if variants and variants[0].get("image_url") else None

    # stock=None en Tiendanube significa "sin control de stock" (ilimitado), no cero
    stock_values = [v.get("stock") for v in available_variants]
    unlimited_stock = any(s is None for s in stock_values)
    total_stock = sum(s for s in stock_values if s is not None)

    return {
        "url": url,
        "name": name,
        "tags": tags,
        "price": min(prices) if prices else None,
        "compare_at_price": max(compare_prices) if compare_prices else None,
        "on_sale": on_sale,
        "total_stock": total_stock,
        "unlimited_stock": unlimited_stock,
        "variants_total": len(variants),
        "variants_available": len(available_variants),
        "image_url": f"https:{image_url}" if image_url else None,
    }


def scrape_catalog(store_url: str, delay: float = 0.5) -> list[dict]:
    urls = get_product_urls(store_url)
    logger.info(f"{len(urls)} productos encontrados en el sitemap")
    products = []
    for url in urls:
        product = scrape_product(url)
        if product:
            products.append(product)
        time.sleep(delay)
    return products


if __name__ == "__main__":
    store_url = sys.argv[1] if len(sys.argv) > 1 else "https://shaffecompany.com.ar"
    catalog = scrape_catalog(store_url)
    out_path = Path(__file__).resolve().parent.parent / "catalog_snapshot.json"
    out_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"{len(catalog)} productos guardados en {out_path}")
