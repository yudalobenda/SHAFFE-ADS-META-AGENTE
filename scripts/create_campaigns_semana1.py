"""
Crea las campañas de Semana 1 en Meta Ads para Shaffe.
Campañas creadas en estado PAUSED para revisión manual antes de activar.

Uso:
    python scripts/create_campaigns_semana1.py --dry-run   # solo muestra qué crearía
    python scripts/create_campaigns_semana1.py             # crea en Meta (estado PAUSED)
"""
import os
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.ad import Ad

# ── Constantes ──────────────────────────────────────────────────────────────
PAGE_ID = "1072917156052129"  # Shaffe Company

PRODUCTS = {
    "babucha_origins": {
        "name": "Babucha Origins",
        "url": "https://shaffecompany.com.ar/productos/babucha-origins-67w72/",
        "image_url": "https://acdn-us.mitiendanube.com/stores/003/381/370/products/img_0351-0f7d80b2d40b9e826917605410564664-1024-1024.webp",
        "price": 32900,
    },
    "buzo_gander": {
        "name": "Buzo Gander",
        "url": "https://shaffecompany.com.ar/productos/buzo-gander-xvjru/",
        "image_url": "https://acdn-us.mitiendanube.com/stores/003/381/370/products/img_1142-e19440b3bc6560793217579652702488-1024-1024.webp",
        "price": 32900,
    },
    "polera_marsella": {
        "name": "Polera Marsella",
        "url": "https://shaffecompany.com.ar/productos/polera-marsella-1ccee/",
        "image_url": "https://acdn-us.mitiendanube.com/stores/003/381/370/products/marsella-negro-6-03818d81e258b6211917745407643049-1024-1024.webp",
        "price": 27500,
    },
}

# Targeting para Buenos Aires, hombres 18-35
TARGETING_BASE = {
    "geo_locations": {
        "countries": ["AR"],
        "cities": [{"key": "2392802", "radius": 40, "distance_unit": "kilometer"}],
    },
    "age_min": 18,
    "age_max": 35,
    "genders": [1],  # 1 = hombre
    "publisher_platforms": ["facebook", "instagram"],
    "facebook_positions": ["feed", "story"],
    "instagram_positions": ["stream", "story", "reels"],
}


def ars_to_api(pesos: int) -> int:
    """ARS en centavos (unidad mínima que usa la API de Meta)."""
    return pesos * 100


def init_api():
    FacebookAdsApi.init(
        app_id=os.getenv("META_APP_ID"),
        app_secret=os.getenv("META_APP_SECRET"),
        access_token=os.getenv("META_ACCESS_TOKEN"),
    )
    return AdAccount(os.getenv("META_AD_ACCOUNT_ID"))


def create_campaign(account: AdAccount, name: str, dry_run: bool) -> str | None:
    params = {
        "name": name,
        "objective": "OUTCOME_TRAFFIC",
        "status": "PAUSED",
        "special_ad_categories": [],
        "is_adset_budget_sharing_enabled": False,
    }
    if dry_run:
        print(f"  [DRY-RUN] Campaña: {name}")
        return "FAKE_CAMPAIGN_ID"
    campaign = account.create_campaign(params=params)
    print(f"  Campaña creada: {campaign['id']} — {name}")
    return campaign["id"]


def create_adset(account: AdAccount, campaign_id: str, name: str,
                 daily_budget_ars: int, targeting: dict, dry_run: bool) -> str | None:
    params = {
        "name": name,
        "campaign_id": campaign_id,
        "billing_event": "IMPRESSIONS",
        "optimization_goal": "LINK_CLICKS",
        "daily_budget": ars_to_api(daily_budget_ars),
        "targeting": targeting,
        "status": "PAUSED",
        "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
    }
    if dry_run:
        print(f"  [DRY-RUN] AdSet: {name} — ${daily_budget_ars}/día")
        return "FAKE_ADSET_ID"
    adset = account.create_ad_set(params=params)
    print(f"  AdSet creado: {adset['id']} — {name} (${daily_budget_ars}/día)")
    return adset["id"]


def create_carousel_creative(account: AdAccount, dry_run: bool) -> str | None:
    babucha = PRODUCTS["babucha_origins"]
    gander = PRODUCTS["buzo_gander"]
    store_url = "https://shaffecompany.com.ar"

    creative_params = {
        "name": "Shaffe — Carrusel Combo Invierno",
        "object_story_spec": {
            "page_id": PAGE_ID,
            "link_data": {
                "link": store_url,
                "message": "El combo de invierno perfecto. Babucha Origins + Buzo Gander, $32.900 cada uno. Envio gratis CABA.",
                "child_attachments": [
                    {
                        "link": gander["url"],
                        "image_url": gander["image_url"],
                        "name": "Buzo Gander",
                        "description": "$32.900 — Ver talles y colores",
                        "call_to_action": {
                            "type": "SHOP_NOW",
                            "value": {"link": gander["url"]},
                        },
                    },
                    {
                        "link": babucha["url"],
                        "image_url": babucha["image_url"],
                        "name": "Babucha Origins",
                        "description": "$32.900 — Ver talles y colores",
                        "call_to_action": {
                            "type": "SHOP_NOW",
                            "value": {"link": babucha["url"]},
                        },
                    },
                    {
                        "link": store_url,
                        "image_url": gander["image_url"],
                        "name": "Ver todo Shaffe",
                        "description": "Envio gratis CABA · shaffecompany.com.ar",
                        "call_to_action": {
                            "type": "SHOP_NOW",
                            "value": {"link": store_url},
                        },
                    },
                ],
                "multi_share_end_card": False,
            },
        },
    }
    if dry_run:
        print("  [DRY-RUN] Creative: Carrusel Combo Invierno")
        return "FAKE_CREATIVE_ID"
    creative = account.create_ad_creative(params=creative_params)
    print(f"  Creative creado: {creative['id']} — Carrusel Combo Invierno")
    return creative["id"]


def create_static_creative(account: AdAccount, dry_run: bool) -> str | None:
    marsella = PRODUCTS["polera_marsella"]
    creative_params = {
        "name": "Shaffe — Polera Marsella Estatica",
        "object_story_spec": {
            "page_id": PAGE_ID,
            "link_data": {
                "link": marsella["url"],
                "message": "Polera manga larga para el invierno. Talles S al XL, colores BLANCO y NEGRO. $27.500. Envio gratis CABA.",
                "image_url": marsella["image_url"],
                "name": "Polera Marsella — $27.500",
                "description": "shaffecompany.com.ar",
                "call_to_action": {
                    "type": "SHOP_NOW",
                    "value": {"link": marsella["url"]},
                },
            },
        },
    }
    if dry_run:
        print("  [DRY-RUN] Creative: Polera Marsella Estática")
        return "FAKE_CREATIVE_ID"
    creative = account.create_ad_creative(params=creative_params)
    print(f"  Creative creado: {creative['id']} — Polera Marsella Estática")
    return creative["id"]


def create_ad(account: AdAccount, name: str, adset_id: str,
              creative_id: str, dry_run: bool):
    params = {
        "name": name,
        "adset_id": adset_id,
        "creative": {"creative_id": creative_id},
        "status": "PAUSED",
    }
    if dry_run:
        print(f"  [DRY-RUN] Ad: {name}")
        return
    ad = account.create_ad(params=params)
    print(f"  Ad creado: {ad['id']} — {name}")


def run(dry_run: bool):
    label = "DRY-RUN" if dry_run else "REAL"
    print(f"\n=== Creando campañas Semana 1 — Shaffe [{label}] ===\n")

    account = None if dry_run else init_api()

    # ── Campaña 1: Carrusel ──────────────────────────────────────────────────
    print(">> Campaña 1: Carrusel — Babucha Origins + Buzo Gander")
    campaign_id_1 = create_campaign(account, "Shaffe — Carrusel Combo Invierno [S1]", dry_run)
    adset_id_1 = create_adset(
        account, campaign_id_1,
        "BsAs | Hombres 20-35 | Combo Invierno",
        daily_budget_ars=2000,
        targeting={**TARGETING_BASE, "age_min": 20, "age_max": 35},
        dry_run=dry_run,
    )
    creative_id_1 = create_carousel_creative(account, dry_run)
    create_ad(account, "Carrusel — Babucha + Gander", adset_id_1, creative_id_1, dry_run)

    print()

    # ── Campaña 2: Imagen estática ───────────────────────────────────────────
    print(">> Campaña 2: Imagen Estática — Polera Marsella")
    campaign_id_2 = create_campaign(account, "Shaffe — Polera Marsella Precio Entrada [S1]", dry_run)
    adset_id_2 = create_adset(
        account, campaign_id_2,
        "BsAs | Hombres 18-35 | Precio Entrada",
        daily_budget_ars=1500,
        targeting=TARGETING_BASE,
        dry_run=dry_run,
    )
    creative_id_2 = create_static_creative(account, dry_run)
    create_ad(account, "Imagen — Polera Marsella", adset_id_2, creative_id_2, dry_run)

    print()
    print("=== Listo ===")
    if not dry_run:
        print("Campañas creadas en estado PAUSED.")
        print("Revisalas en Meta Ads Manager y activá cuando estes listo.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    run(dry_run=args.dry_run)
