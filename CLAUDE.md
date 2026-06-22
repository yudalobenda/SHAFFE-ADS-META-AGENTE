# SHAFFE ADS AGENT — Claude Code Context

## Quién soy y qué estamos construyendo

Soy León, dueño de **SHAFFECO (SHF S.A.)**, la marca de ropa urbana/streetwear argentina **Shaffe** (shaffecompany.com.ar). Este proyecto es un sistema multi-agente de gestión publicitaria que actúa como una agencia de marketing real y autónoma para Shaffe, con arquitectura reutilizable para otras cuentas/marcas en el futuro.

El sistema se llama **SHAFFE ADS AGENT**.

---

## Stack y decisiones ya tomadas

- **Lenguaje**: Python 3.11+
- **Infraestructura**: GitHub Actions (scheduler principal, corre lunes 9am Argentina)
- **Base de datos**: PostgreSQL (historial, aprendizaje acumulativo, logs de decisiones)
- **Notificaciones y aprobaciones**: Telegram Bot (inline buttons para aprobar/rechazar)
- **Dashboard**: Web app (React + FastAPI o similar) para visualización de métricas e historial
- **IA**: Claude API (claude-sonnet) como cerebro analítico de cada agente
- **Autonomía**: Híbrido — el agente analiza solo, pero para cambiar presupuesto o lanzar nuevos ads me pide aprobación por Telegram
- **Arquitectura**: Multi-cuenta desde el arranque (preparado para funcionar como agencia con múltiples clientes)

---

## Plataformas publicitarias (orden de prioridad)

1. **Meta Ads** (Facebook + Instagram) — ARRANCAR ACÁ
2. **Google Ads** (Search + Display)
3. **TikTok Ads**
4. **Google Shopping** (último)

---

## Agentes del sistema

### AGENTE 1 — ROAS Agent
- Monitorea ROAS real por campaña / adset / ad individual
- Compara contra target configurado por cuenta
- Propone pausar, escalar o mantener → manda a Telegram para aprobación
- Fuente de datos: Meta Ads API (real, sin inventar)

### AGENTE 2 — Budget Agent
- Reasigna presupuesto entre campañas según performance
- Detecta campañas quemando plata sin resultado
- Propone redistribución → espera aprobación mía antes de ejecutar

### AGENTE 3 — Audience Agent
- Testea en paralelo: Retargeting vs Lookalike vs Frío (interés/comportamiento)
- Monitorea CPM, frecuencia de impresión, saturación de audiencia
- Detecta cuándo una audiencia se agotó y propone alternativas

### AGENTE 4 — Competitor Intelligence Agent
- Usa **Meta Ad Library API** (pública, sin scraping ilegal) para espiar competidores
- Extrae: qué formatos usan, qué copy, hace cuánto están activos (tiempo activo = funciona)
- Lista de competidores a seguir: configurable por cuenta en `config/accounts.yaml`
- Output: resumen semanal "esto es lo que está funcionando en tu nicho ahora"

### AGENTE 5 — Trend Agent
- Detecta qué ads del nicho streetwear/moda Argentina llevan más tiempo activos en Ad Library
- Analiza formatos predominantes: Reel vs carrusel vs imagen estática
- Cruza con TikTok Creative Center API para detectar tendencias de sonidos y hooks

### AGENTE 6 — Content Intelligence Agent ← EL MÁS IMPORTANTE
Este no es un "probador de variantes". Es el director creativo autónomo de Shaffe.

**Cada semana hace esto:**

**A) Analiza el catálogo real de shaffecompany.com.ar**
- Scraping de productos activos: nombre, precio, stock, categoría, imagen
- Cruza con métricas de Meta Ads: qué productos tuvieron más CTR, cuáles convirtieron, cuáles nunca se promocionaron
- Genera ranking: "estos son los productos con mayor potencial para publicitar esta semana y por qué"

**B) Analiza competencia y tendencias**
- Qué están promocionando marcas similares
- Qué formatos predominan esta semana en el nicho
- Qué hooks/ganchos están funcionando

**C) Genera el plan de contenido semanal completo**

Output por Telegram + dashboard, ejemplo real:

```
📅 PLAN SEMANA 24 — SHAFFE

🎯 PRODUCTO ESTRELLA: Buzo cargo oliva $34.900
Motivo: 3.2% CTR en última campaña, stock alto, competencia no lo trabaja

📹 VIDEO 1 — Reel 15s (Instagram + Facebook)
Gancho: "El buzo que nadie tiene pero todos van a querer"
Seg 0-2:  Plano cerrado textura cargo. Sin audio. Texto superpuesto.
Seg 2-5:  Outfit completo. Cámara lenta girando. Texto: "$34.900"
Seg 5-10: 3 colores en corte rápido
Seg 10-15: CTA hablado: "Entrá a shaffe.com, te lo mandamos hoy"
Público objetivo: Frío / interés streetwear BsAs / 18-28
Presupuesto sugerido: $8.000/día
KPI a monitorear: CTR > 2.5%, ROAS > 3x

📹 VIDEO 2 — Reel 30s (mismo producto, gancho diferente)
Gancho: "Cómo armar 3 outfits con una sola prenda"
[guion segundo a segundo completo]

🖼️ CARRUSEL 1 — Remera oversize (producto secundario)
Slide 1: Producto solo, fondo blanco
Slide 2: Outfit urbano completo
Slide 3: Precio + "envío gratis CABA"
Slide 4: "Ver todos los talles →"

📊 LÓGICA DE TEST SEMANA 24:
Video 1 vs Video 2 → mismo presupuesto, 4 días
Si CTR Video 1 > 2.5% a los 4 días → escalar x2
Si no → pausar y reportar por qué falló (copy? público? gancho?)
```

**D) Aprende semana a semana**
- Guarda en PostgreSQL: qué guion se usó, métricas resultantes, público, producto
- Después de 4 semanas detecta patrones: "hooks de precio > hooks de lifestyle en tu cuenta", "carruseles convierten mejor en retargeting que en frío"
- El aprendizaje alimenta los guiones siguientes → se vuelve más preciso con el tiempo
- NUNCA inventa datos. Todo análisis se basa en métricas reales de la API

### AGENTE 7 — Telegram Notifier + Approver
- Manda resumen semanal cada lunes
- Alertas en tiempo real si alguna campaña cae fuera de parámetros
- Inline buttons: ✅ Aprobar / ❌ Rechazar / 🔄 Ver más detalle
- Log de todas las decisiones tomadas (aprobadas o rechazadas) en PostgreSQL

---

## Estructura de carpetas del proyecto

```
shaffe-ads-agent/
├── CLAUDE.md                    # Este archivo
├── README.md
├── .env.example                 # Variables de entorno (nunca commitear .env real)
├── requirements.txt
├── config/
│   └── accounts.yaml            # Configuración multi-cuenta (Shaffe + futuras marcas)
├── agents/
│   ├── roas_agent.py
│   ├── budget_agent.py
│   ├── audience_agent.py
│   ├── competitor_agent.py
│   ├── trend_agent.py
│   ├── content_intelligence_agent.py
│   └── telegram_agent.py
├── connectors/
│   ├── meta_ads_api.py          # Wrapper Meta Marketing API
│   ├── google_ads_api.py        # Wrapper Google Ads API
│   ├── tiktok_ads_api.py        # Wrapper TikTok Ads API (Fase 3)
│   ├── meta_ad_library.py       # Meta Ad Library API (competencia)
│   └── tiendanube_scraper.py    # Scraping catálogo shaffecompany.com.ar
├── database/
│   ├── models.py                # SQLAlchemy models
│   ├── migrations/              # Alembic migrations
│   └── queries.py               # Queries frecuentes
├── dashboard/
│   ├── backend/                 # FastAPI
│   └── frontend/                # React
├── scheduler/
│   └── weekly_run.py            # Entry point GitHub Actions
├── utils/
│   ├── claude_client.py         # Wrapper Claude API para análisis
│   └── logger.py
└── .github/
    └── workflows/
        └── weekly_ads_agent.yml # GitHub Actions — lunes 9am ART
```

---

## Variables de entorno necesarias (.env)

```env
# Meta Ads
META_APP_ID=
META_APP_SECRET=
META_ACCESS_TOKEN=
META_AD_ACCOUNT_ID=          # formato: act_XXXXXXXXX

# Google Ads
GOOGLE_ADS_DEVELOPER_TOKEN=
GOOGLE_ADS_CLIENT_ID=
GOOGLE_ADS_CLIENT_SECRET=
GOOGLE_ADS_REFRESH_TOKEN=
GOOGLE_ADS_CUSTOMER_ID=

# TikTok Ads (Fase 3)
TIKTOK_APP_ID=
TIKTOK_SECRET=
TIKTOK_ACCESS_TOKEN=

# Telegram
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Base de datos
DATABASE_URL=postgresql://user:password@localhost:5432/shaffe_ads

# Claude API
ANTHROPIC_API_KEY=

# Tienda
TIENDANUBE_STORE_URL=https://shaffecompany.com.ar
```

---

## Configuración multi-cuenta (config/accounts.yaml)

```yaml
accounts:
  - id: shaffe
    name: Shaffe
    meta_ad_account: act_XXXXXXXXX
    store_url: https://shaffecompany.com.ar
    roas_target: 3.0
    weekly_budget_ars: 50000
    competitors:
      - nombre_pagina_fb_competidor_1
      - nombre_pagina_fb_competidor_2
    audiences:
      retargeting: true
      lookalike: true
      cold: true
    telegram_chat_id: TU_CHAT_ID
```

---

## Fases de construcción

### FASE 1 — Meta Ads base (ARRANCAR ACÁ)
- [ ] Estructura de carpetas y archivos base
- [ ] Conector Meta Ads API (autenticación + fetch campañas reales)
- [ ] ROAS Agent funcional con data real
- [ ] Budget Agent con propuestas
- [ ] Telegram Bot: notificaciones + inline buttons aprobación
- [ ] GitHub Actions: scheduler lunes 9am ART
- [ ] PostgreSQL: schema inicial + logging de decisiones

### FASE 2 — Content Intelligence
- [ ] Scraper catálogo shaffecompany.com.ar (Tiendanube)
- [ ] Cruce catálogo × métricas Meta Ads
- [ ] Generación de plan semanal de contenido con guiones completos
- [ ] Competitor Agent con Meta Ad Library API
- [ ] Learning loop: guardar resultados y aprender

### FASE 3 — Google Ads
- [ ] Google Ads API connector
- [ ] Search Agent + Display Agent
- [ ] Negative keywords detection

### FASE 4 — Dashboard web
- [ ] FastAPI backend
- [ ] React frontend: tabla campañas, gráfico ROAS, creative testing, log de decisiones

### FASE 5 — TikTok Ads
- [ ] TikTok Ads API connector
- [ ] Hook rate analysis (primeros 3 segundos)
- [ ] Cross-platform insights

---

## Reglas importantes para Claude Code

1. **NUNCA inventar datos**. Si la API no devuelve algo, loguearlo y reportarlo. Cero alucinación de métricas.
2. **Siempre pedir aprobación antes de**: cambiar presupuesto, pausar campaña, lanzar nueva ad.
3. **Autonomía permitida sin aprobación**: lectura de datos, generación de reportes, generación de guiones de contenido.
4. **Multi-cuenta desde el arranque**: toda la lógica debe estar parametrizada por `account_id`, nunca hardcodeada para Shaffe.
5. **Logs de todo**: cada decisión del agente (qué analizó, qué propuso, si fue aprobada) va a PostgreSQL.
6. **Idioma de outputs**: español rioplatense (los reportes de Telegram son para León, argentino).
7. **Arrancar siempre por Fase 1** antes de avanzar a siguientes fases.

---

## Cómo arrancar (Fase 1, primer día)

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Instalar dependencias base
pip install facebook-business anthropic python-telegram-bot sqlalchemy alembic psycopg2-binary pyyaml python-dotenv requests

# 3. Copiar .env.example a .env y completar credenciales
cp .env.example .env

# 4. Crear base de datos PostgreSQL
createdb shaffe_ads

# 5. Correr migraciones iniciales
alembic upgrade head

# 6. Test de conexión Meta API
python connectors/meta_ads_api.py --test

# 7. Correr el agente en modo dry-run (sin ejecutar cambios)
python scheduler/weekly_run.py --dry-run
```

---

## Contexto de negocio Shaffe

- **Marca**: Shaffe — ropa urbana/streetwear argentina
- **Tienda**: shaffecompany.com.ar (Tiendanube)
- **MercadoLibre**: Seller Platinum, ID 262443439
- **Canales sociales**: Instagram, TikTok, WhatsApp Business
- **Público target**: 18-30 años, urbano, Buenos Aires y AMBA
- **Identidad visual**: paleta muted (negro, off-white, beige, oliva), locaciones urbanas BsAs
- **Formatos de contenido activos**: Reels 15-30s, carruseles, imágenes estáticas
- **Producción de contenido**: equipo interno

---

## Primer mensaje para darle a Claude Code al abrir la terminal

Una vez que estés en la carpeta `shaffe-ads-agent/` con este CLAUDE.md adentro, Claude Code va a leer todo este contexto automáticamente. Simplemente decile:

> "Arrancá la Fase 1. Creá la estructura de carpetas completa, el conector de Meta Ads API con autenticación OAuth, y el ROAS Agent básico que traiga datos reales de campañas. Usá las variables del .env.example."
