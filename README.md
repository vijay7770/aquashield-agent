# 🛡️ AquaShield — AI Agent Built with IBM Bob

> **The developer workflow problem: building a multi-component AI agent system from scratch takes days. With IBM Bob's Agent mode, AquaShield went from zero to a fully deployed watsonx Orchestrate agent in under 8 hours.**

Built for the **IBM TechXchange 2026 Hackathon** using **IBM Bob v2.0.3** as the primary development tool.

🔗 **[Live Demo](https://vijay7770.github.io/aquashield-agent/)** &nbsp;|&nbsp; 🎬 **[Watch Demo Video](https://www.youtube.com/watch?v=nQNaUQrbbsc)**

---

## 🧑‍💻 The Developer Workflow Problem This Solves

Building a production AI agent system normally requires a developer to:

- Scaffold a Flask app, write data models, error handlers, and CORS setup manually
- Implement IBM IAM token auth + watsonx.ai REST API calls from scratch
- Learn and implement the Orchestrate ADK `@tool` decorator contract correctly
- Debug container builds, environment variable injection, and IBM Code Engine deployment
- Write OpenAPI specs, YAML agent manifests, and iterate on Granite prompts

**This bottleneck kills developer productivity.** Every hour spent on integration boilerplate is an hour not spent on the AI logic that differentiates the solution.

**AquaShield demonstrates the answer:** using IBM Bob's Agent mode, every one of these components was generated, debugged, and deployed through natural language — **56 Bob tasks, 100% in Agent mode**. A fully working, cloud-deployed AI agent system with IBM watsonx.ai integration — built in under 8 hours, not days.

---

## 🎬 Demo Video

[![Watch the AquaShield Demo](https://img.shields.io/badge/▶%20Watch%20Demo%20Video-AquaShield%20%7C%20IBM%20TechXchange%202026-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/watch?v=nQNaUQrbbsc)

> One sentence in. Decision-ready plan out. Watch AquaShield turn a chlorine supplier strike into a 60-second AI action brief — live in watsonx Orchestrate.

---

## What It Does (The Solution Bob Built)

AquaShield is a supply chain disruption response agent for water utility procurement managers. It demonstrates that IBM Bob can produce a **complete, multi-layer AI agent system** from natural language instructions.

| Output | Description |
|--------|-------------|
| 🎯 **Criticality Assessment** | CRITICAL / HIGH / MEDIUM / LOW based on stock days vs delay |
| 🚨 **EPA Compliance Alert** | Days-to-stockout countdown for health-critical chemicals |
| 🔄 **Alternative Suppliers** | Vetted backups ranked by reliability score + direct contact |
| 📋 **Action Plan** | Numbered immediate steps for the procurement manager |
| 🧠 **AI Risk Assessment** | IBM Granite narrative using live data + historical patterns |
| 📝 **Executive Summary** | Director-ready paragraph for email escalation |
| ⚡ **Time Saved** | ~3 hours manual → under 60 seconds AI |

---

## 🤖 How IBM Bob Was Used — Developer Workflow in Practice

Bob was not used to autocomplete lines of code — **Bob was the developer.** Every file was created through a Bob Agent mode task.

### 56 Tasks, 100% Agent Mode

| Bob Capability | Where Applied |
|----------------|---------------|
| **Agent mode** — full file generation | `src/agent.py`, `src/watsonx_client.py`, `src/app.py` — each written as a single task |
| **Agent mode** — multi-file scaffolding | Project structure, `requirements.txt`, `.gitignore`, `.bobignore`, `.env.example` in one task |
| **Agent mode** — MCP tool use | Bob called the watsonx Orchestrate MCP (`create_or_update_agent`, `import_tool`) to deploy without leaving VS Code |
| **Agent mode** — iterative debugging | Bob read error output, identified the fix, applied it — all within the same task |
| **Agent mode** — data generation | All three JSON data files generated with realistic domain content |
| **Agent mode** — containerisation | `Dockerfile` + `.dockerignore` + Code Engine deployment commands |
| **Agent mode** — documentation | README, OpenAPI spec, and agent YAML written by Bob |

### Where Bob Saved the Most Time

| Task | Without Bob | With Bob |
|------|-------------|----------|
| IBM IAM token auth + caching | 45–60 min | 1 Bob task |
| Orchestrate ADK `@tool` decorator | 30–60 min | 1 Bob task |
| Criticality scoring algorithm | 60–90 min | 1 Bob task |
| Docker + Code Engine deploy | 60 min | 1 Bob task |
| GitHub Pages demo site + embed | 120–180 min | 1 Bob task |
| **Total saved** | **~12–15 hours** | **56 tasks** |

---

## 📊 Bob Usage Evidence

| Metric | Value |
|--------|-------|
| Bob tasks completed | **56** |
| Bob mode | **100% Agent mode** |
| Bob language contributions | YAML 75.95%, config/text 24.05% |
| Session screenshots | [`bob-sessions/`](bob-sessions/) |
| Bobalytics export | [`docs/bobalytics_export_user_2026-07-31_2026-08-29/`](docs/bobalytics_export_user_2026-07-31_2026-08-29/) |

---

## System Architecture

```
User (natural language)
  └─▶ watsonx Orchestrate Agent  (aquashield_agent)
        └─▶ runDisruptionResponse tool  (tools/disruption_tool.py)
              └─▶ IBM Code Engine  POST /api/disruption
                    ├─▶ AquaShieldAgent.analyse()  (src/agent.py)
                    │     ├── Criticality scoring
                    │     ├── Health risk / EPA compliance flag
                    │     ├── Historical pattern context
                    │     └── Alternative supplier matching
                    └─▶ WatsonXClient  (src/watsonx_client.py)
                          └─▶ IBM Granite (ibm/granite-4-h-small)
                                ├── generate_risk_assessment()
                                └── generate_executive_summary()
```

---

## Try It — 5 Starter Prompts

| # | Scenario | Severity |
|---|----------|----------|
| 1 | `Supplier SUP-001 (Liquid Chlorine) has had a factory fire. They will be delayed 14 days.` | 🔴 CRITICAL |
| 2 | `SUP-003 port strike affecting coagulant shipments — 7-day delay. Assess impact.` | 🟠 HIGH |
| 3 | `Sodium fluoride SUP-002 delayed 5 days — how critical and what should I do?` | 🟠 HIGH |
| 4 | `SUP-004 pump supplier declared bankruptcy. 30-day disruption. What are our alternatives?` | 🟡 MEDIUM |
| 5 | `SUP-005 semiconductor shortage — 21-day sensor delay across 3 monitoring stations.` | 🟢 LOW |

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Primary Dev Tool | **IBM Bob v2.0.3** (56 tasks, 100% Agent mode) |
| Agent Platform | IBM watsonx Orchestrate (native agent, react_core) |
| LLM — Agent | IBM Granite |
| LLM — Risk/Summary | IBM watsonx.ai `ibm/granite-4-h-small` |
| Backend API | Python 3.11, Flask, IBM Code Engine |
| ADK | `ibm-watsonx-orchestrate==2.15.0` |
| API Spec | OpenAPI 3.0 |
| Container | Docker |

---

## Run Locally

```bash
# 1. Clone and set up environment
cd aquashield-agent
cp .env.example .env
# Edit .env with your IBM credentials

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the Flask backend
python src/app.py        # listens on PORT (default 8080)

# 4. Test the API
curl -X POST http://localhost:8080/api/disruption \
  -H "Content-Type: application/json" \
  -d '{"supplier_id":"SUP-001","description":"Factory fire","delay_days":14}'
```

### Environment Variables

```
IBM_API_KEY          # IBM Cloud API key
WATSONX_URL          # e.g. https://us-south.ml.cloud.ibm.com
WATSONX_PROJECT_ID   # watsonx.ai project ID
CODE_ENGINE_URL      # Deployed Code Engine URL (used by disruption_tool.py)
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/disruption` | Analyse a disruption — returns full action plan |
| `GET` | `/api/suppliers` | List all suppliers with risk data |
| `GET` | `/api/orders` | List all open orders |
| `GET` | `/api/status` | Health check with supplier/order counts |

---

## Key Files

| File | Purpose | Bob task? |
|------|---------|-----------|
| `src/agent.py` | Core disruption analysis logic | ✅ 1 task |
| `src/watsonx_client.py` | IBM Granite client with IAM token caching | ✅ 1 task |
| `src/app.py` | Flask API entry point | ✅ 1 task |
| `tools/disruption_tool.py` | watsonx Orchestrate ADK tool | ✅ 1 task |
| `agents/aquashield_agent.yaml` | Orchestrate agent spec | ✅ 1 task |
| `data/suppliers.json` | 8 suppliers with reliability scores | ✅ 1 task |
| `data/orders.json` | 7 open purchase orders | ✅ 1 task |
| `data/disruptions.json` | Historical disruption records | ✅ 1 task |
| `demo/index.html` | Live demo page with embedded Orchestrate widget | ✅ 1 task |
| `Dockerfile` | IBM Code Engine container | ✅ 1 task |
| `openapi.yaml` | OpenAPI 3.0 spec | ✅ 1 task |

---

*AquaShield · IBM TechXchange 2026 Hackathon · Built with IBM Bob v2.0.3 · 56 tasks · 100% Agent mode*
