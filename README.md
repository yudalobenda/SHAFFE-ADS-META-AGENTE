# Shaffe Ads Agent — Fase 1

Sistema multi-agente de gestión publicitaria para Shaffe. Ver `CLAUDE.md` para el contexto completo del proyecto.

## Qué incluye esta fase

- Conector real a Meta Marketing API (`connectors/meta_ads_api.py`)
- ROAS Agent: compara ROAS real por campaña contra el target de la cuenta (`agents/roas_agent.py`)
- Budget Agent: propone redistribuir presupuesto de campañas a pausar hacia las que escalan (`agents/budget_agent.py`)
- Telegram Bot: manda propuestas con botones ✅ Aprobar / ❌ Rechazar (`agents/telegram_agent.py`)
- PostgreSQL: schema de cuentas y log de decisiones (`database/models.py`, Alembic en `database/migrations/`)
- GitHub Actions: corre el scheduler todos los lunes 9am ART (`.github/workflows/weekly_ads_agent.yml`)

## Setup

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt

copy .env.example .env         # completar credenciales reales
createdb shaffe_ads
alembic revision --autogenerate -m "schema inicial"
alembic upgrade head

python connectors/meta_ads_api.py --test
python scheduler/weekly_run.py --dry-run
```

## Importante: el listener de aprobaciones de Telegram es un proceso separado

GitHub Actions corre el scheduler una vez por semana y termina — no puede quedarse escuchando los clicks de los botones de Telegram. Para que ✅/❌ funcionen hay que correr, en algún lugar que esté siempre prendido (un server propio, Railway, un VPS chico, etc.):

```bash
python agents/telegram_agent.py
```

Eso deja un bot escuchando `CallbackQueryHandler` y actualiza el estado de la decisión en PostgreSQL cuando León aprueba o rechaza.

## Pendiente fuera de Fase 1

Audience Agent, Competitor Intelligence Agent, Trend Agent, Content Intelligence Agent, conectores de Google Ads / TikTok Ads / Tiendanube y el dashboard quedan para las fases siguientes (ver `CLAUDE.md`).
