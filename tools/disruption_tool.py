# =============================================================================
# AquaShield — IBM watsonx Orchestrate ADK Tool
# File: tools/disruption_tool.py
#
# Deploy via:
#   wxo-cli tool deploy tools/disruption_tool.py
# =============================================================================

import os

import requests
from dotenv import load_dotenv
from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission

load_dotenv()


@tool(
    name="runDisruptionResponse",
    description=(
        "Analyze a supply chain disruption at a water utility. "
        "Returns affected orders, criticality assessment, alternative suppliers, "
        "action plan with immediate steps, AI risk assessment, and executive summary."
    ),
    permission=ToolPermission.READ_ONLY,
)
def run_disruption_response(
    supplier_id: str,
    description: str,
    delay_days: int,
) -> dict:
    """Call the AquaShield backend disruption endpoint and return the full analysis."""
    base_url = os.getenv(
        "CODE_ENGINE_URL",
        "https://aquashield-agent.2e2mqn500xa7.us-south.codeengine.appdomain.cloud"
    ).rstrip("/")
    try:
        response = requests.post(
            f"{base_url}/api/disruption",
            json={
                "supplier_id": supplier_id,
                "description": description,
                "delay_days": delay_days,
            },
            timeout=60,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}
