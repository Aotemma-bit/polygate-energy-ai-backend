# Polygate Energy AI — Frontend

A production-deployed operations interface for **Polygate Energy AI**, an AI engineering platform concept for oil & gas and industrial energy operations.

## What this application demonstrates

Polygate Energy AI brings operational data, engineering knowledge, AI-assisted retrieval, realtime telemetry, and predictive analytics into one interface.

### FieldFlow

FieldFlow is the engineering knowledge interface.

It combines:
- Retrieval-augmented generation (RAG)
- Vector search
- OpenAI embeddings
- Grounded answers from indexed oil & gas documents
- Source/page citations
- Streaming responses

The objective is to help engineers retrieve relevant technical information using natural language while keeping generated answers tied to indexed source material.

### Operations Command Center

The Operations interface provides:
- Equipment risk visibility
- Sensor trend monitoring
- Operational attention signals
- Maintenance-event intelligence
- Engineering decision queues
- Realtime sensor updates
- Polling fallback

The current demonstration uses equipment **C-104** and a simulated telemetry stream. It is a demonstration and should not be interpreted as a production monitoring system or real field deployment.

### Polygate Predict

Predict combines:
- Sensor trend analysis
- Transparent anomaly scoring
- Maintenance-history signals
- Engineering action recommendations
- A separate benchmark machine-failure model based on the UCI AI4I 2020 Predictive Maintenance Dataset

The benchmark model is intentionally kept separate from the C-104 field telemetry because its training features are different. It is a benchmark/portfolio model and is **not validated for real-world field deployment**.

## Why this matters to oil & gas companies

Oil & gas operations generate large volumes of information across equipment telemetry, maintenance records, engineering documents, operating procedures, asset data, and operational systems.

This architecture demonstrates a way to bring those information sources closer together:

**Operational data → detection → engineering context → decision support**

Potential enterprise use cases include:

- **Faster engineering information retrieval:** engineers can ask technical questions in natural language and receive answers tied to indexed source material.
- **Earlier visibility into changing operating conditions:** telemetry can surface directional changes in vibration, temperature, pressure, and flow.
- **Maintenance intelligence:** historical maintenance findings can be considered alongside current operating signals.
- **Reduced information fragmentation:** dashboards, technical knowledge, and analytical outputs can be accessed through one application.
- **Decision support:** the system exposes observed signals, supporting evidence, and suggested engineering review rather than only displaying a single opaque score.
- **Integration foundation:** the same architecture could be extended to additional assets, historians, maintenance systems, document repositories, and enterprise APIs.

These are potential applications demonstrated by the architecture, not claims of measured production ROI or guaranteed operational outcomes.

## Tech stack

| Layer | Technology | Role |
|---|---|---|
| Frontend | Next.js / React / TypeScript | Production web application |
| UI | Tailwind CSS | Operations-focused interface |
| Charts | Recharts | Sensor and operational visualization |
| Realtime | Supabase JavaScript client | Live database change subscriptions |
| Backend API | FastAPI / Python | API, orchestration, analytics |
| Database | PostgreSQL / Supabase | Operational/application data |
| Vector search | Supabase / pgvector | Semantic document retrieval |
| AI | OpenAI embeddings + LLM | RAG embeddings and grounded responses |
| ML | scikit-learn / joblib | Benchmark predictive-maintenance model |
| Explainability | SHAP | ML model explanation |
| Deployment | Vercel + FastAPI Cloud | Production hosting |
| Source control | Git / GitHub | Version control |

## Architecture

```text
                         ┌──────────────────────────┐
                         │       Next.js Frontend   │
                         │                          │
                         │ FieldFlow                │
                         │ Operations               │
                         │ Polygate Predict         │
                         └────────────┬─────────────┘
                                      │ HTTPS
                                      ▼
                         ┌──────────────────────────┐
                         │       FastAPI API        │
                         │                          │
                         │ RAG / AI                 │
                         │ Operations Intelligence  │
                         │ Predictive Analytics     │
                         └────────────┬─────────────┘
                                      │
                       ┌──────────────┴──────────────┐
                       ▼                             ▼
              ┌─────────────────┐          ┌─────────────────┐
              │ Supabase /      │          │ OpenAI          │
              │ PostgreSQL      │          │ Embeddings/LLM  │
              │ + pgvector      │          └─────────────────┘
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Sensor          │
              │ Telemetry       │
              └─────────────────┘
```

## Local development

```bash
npm install
npm run dev
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

Do not commit `.env.local` or production secrets.

## Production

Production frontend:

**https://polygate-energy-ai-frontend.vercel.app**

The frontend communicates with the separately deployed FastAPI backend through `NEXT_PUBLIC_API_URL`.

## Limitations

This repository is a portfolio / engineering demonstration.

- C-104 telemetry is simulated.
- The predictive trend engine is decision-support logic, not a validated industrial diagnostic system.
- The benchmark ML model uses the UCI AI4I 2020 Predictive Maintenance Dataset and is not validated for real-world field deployment.
- The project does not claim measured production savings, reliability improvement, safety performance, or production increases.

## Repositories

- Frontend: `polygate-energy-ai-frontend`
- Backend: `polygate-energy-ai-backend`
