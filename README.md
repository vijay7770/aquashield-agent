# 🛡️ AquaShield — AI Supply Chain Disruption Response Agent

> **100,000 people's drinking water. One delayed shipment. AquaShield turns a 3-hour manual crisis into a 60-second AI decision.**

Built for the **IBM TechXchange 2026 Hackathon** using **IBM Bob** as the primary development tool.

🔗 **[Live Demo](https://vijay7770.github.io/aquashield-agent/)** &nbsp;|&nbsp; 💬 **[Chat with AquaShield](https://vijay7770.github.io/aquashield-agent/)**

---

## What It Does

Water utilities depend on critical chemical suppliers — liquid chlorine, sodium fluoride, coagulants — for **EPA Safe Drinking Water Act compliance**. When a supplier delays, procurement teams spend hours manually calling backups, checking spreadsheets, and drafting escalation emails.

**AquaShield** accepts a single natural-language disruption report and instantly returns:

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
| Primary Dev Tool | **IBM Bob v2.0.3** (wrote every file via natural language) |
| Agent Platform | IBM watsonx Orchestrate (native agent, react_core) |
| LLM — Agent | `groq/openai/gpt-oss-120b` |
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

| File | Purpose |
|------|---------|
| `src/agent.py` | Core disruption analysis logic — criticality scoring, EPA flags, action plans |
| `src/watsonx_client.py` | IBM Granite client with IAM token caching and offline fallback |
| `src/app.py` | Flask API entry point |
| `tools/disruption_tool.py` | watsonx Orchestrate ADK tool — calls Code Engine |
| `agents/aquashield_agent.yaml` | Orchestrate agent spec |
| `data/suppliers.json` | 8 suppliers with reliability scores, stock levels, backup IDs |
| `data/orders.json` | 7 open purchase orders |
| `data/disruptions.json` | Historical disruption records with lessons learned |
| `docs/demo.html` | Live demo page with embedded Orchestrate chat widget |

---

## Built with IBM Bob

Every source file, the watsonx Orchestrate connection via MCP, the Code Engine deployment, and this README were all created through **IBM Bob** — an AI coding assistant — using only conversational natural-language prompts. This project demonstrates AI building an AI agent system, end-to-end, in under 8 hours.

---

*AquaShield · IBM TechXchange 2026 Hackathon · Built with IBM Bob v2.0.3*
