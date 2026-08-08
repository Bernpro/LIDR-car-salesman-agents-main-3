# 🚗 CarBot Pro - Sistema Multiagente de Ventas de Coches

App de Streamlit que simula un vendedor de coches (Carlos) apoyado por un
sistema multi-agente (María en investigación, Edu como manager coordinador),
con búsqueda inteligente sobre un inventario real.

Incluye **tres modos**, seleccionables desde la barra lateral:

| Modo | Necesita API key | Coste | IA real | Inventario real |
|---|---|---|---|---|
| 🎮 Demo | No | Gratis | No (plantillas) | Sí |
| ⚡ Groq | Sí (gratis) | Gratis | Sí (modelos Llama) | Sí |
| 🤖 OpenAI | Sí (de pago) | De pago | Sí (modelos GPT) | Sí |

## Estructura

- **`enhanced_app.py`** — interfaz principal de Streamlit (chat, perfil de
  cliente, tabla de inventario, logs de debug, comunicación entre agentes).
  **Este es el archivo que ejecutas.**
- `advanced_multi_agent_system.py` — sistema real con LangChain + OpenAI.
- `advanced_multi_agent_system_groq.py` — sistema real con LangChain + **Groq** (gratis).
- `demo_car_sales_system.py` — modo demo: sin LLM, pero con búsquedas reales
  sobre el inventario.
- `enhanced_inventory_manager.py` — motor de búsqueda inteligente de inventario
  (no requiere ninguna API key, usa pandas + reglas).
- `data/enhanced_inventory.csv` — inventario de ejemplo (105 vehículos
  generados automáticamente). Sustitúyelo por tu propio inventario respetando
  las mismas columnas: `year, make, model, body_styles, color, mileage, price,
  fuel_type, engine, transmission, safety_rating, trunk_space_liters, features,
  condition, location, vin`.
- `test_system.py` — script para verificar que todo funciona (`python test_system.py`).
- `requirements.txt` — dependencias, con versiones fijadas.

> ⚠️ **Nota de compatibilidad:** este proyecto usa la API "legacy" de agentes de
> LangChain (`create_react_agent`, `AgentExecutor`), que **no funciona** con
> LangChain 1.x. Por eso `requirements.txt` fija versiones exactas
> (`langchain==0.2.16`, etc.) — no las actualices sin adaptar el código.

## Instalación local

```bash
git clone <url-de-tu-repo>
cd <tu-repo>
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Probar que todo funciona

```bash
python test_system.py
```

Esto verifica las importaciones, el inventario, la búsqueda y el modo demo sin
necesitar ninguna API key. Si además tienes `OPENAI_API_KEY` en tu `.env`,
también prueba el sistema real.

## Conseguir una API key gratuita de Groq

1. Entra a [console.groq.com/keys](https://console.groq.com/keys) y crea una cuenta (gratis).
2. Genera una nueva API key (empieza con `gsk_...`).
3. El nivel gratuito tiene límites de peticiones por minuto/día, más que
   suficiente para probar la app — usa modelos Llama de Meta.

## Configuración de API keys (solo para los modos Groq / OpenAI)

1. Copia `.env.example` a `.env`:
   ```bash
   cp .env.example .env
   ```
2. Edita `.env` y añade tus claves reales (`GROQ_API_KEY` y/o `OPENAI_API_KEY`).
3. **Nunca subas el archivo `.env` a GitHub** (ya está excluido en `.gitignore`).

## Ejecutar la app

```bash
streamlit run enhanced_app.py
```

Se abrirá en `http://localhost:8501`. En la barra lateral eliges el modo
(Demo / Groq / OpenAI), pegas la API key si hace falta, y pulsas
**"🚀 Inicializar Sistema Avanzado"**.

## Desplegar en Streamlit Community Cloud

1. Sube este repo a GitHub (ver sección siguiente).
2. Entra a [share.streamlit.io](https://share.streamlit.io) y conecta tu repo.
3. Selecciona `enhanced_app.py` como archivo principal.
4. Si vas a usar el modo Groq u OpenAI, añade tus claves en **Settings → Secrets**, por ejemplo:
   ```toml
   GROQ_API_KEY = "gsk_..."
   OPENAI_API_KEY = "sk-..."
   SERPAPI_API_KEY = "..."
   ```
   (el modo demo no necesita nada de esto).

## Subir este proyecto a GitHub

```bash
git init
git add .
git commit -m "Sistema multiagente de ventas de coches (Demo/Groq/OpenAI)"
git branch -M main
git remote add origin https://github.com/tu-usuario/tu-repo.git
git push -u origin main
```
