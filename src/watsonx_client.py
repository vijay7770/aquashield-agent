# =============================================================================
# AquaShield — Supply Chain Disruption Response Agent
# File: src/watsonx_client.py
#
# Purpose:
#   Thin wrapper around the IBM WatsonX.ai REST API.
#   Handles IAM authentication (with token caching) and text-generation
#   requests via the watsonx.ai inference endpoint.
# =============================================================================

import os
import time
import logging

import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

_IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"
_WATSONX_API_VERSION = "2024-05-01"
_MODEL_ID = "ibm/granite-4-h-small"


class WatsonXClient:
    """
    Client for IBM WatsonX.ai foundation-model text generation.

    Reads credentials from environment variables (loaded via python-dotenv):
        IBM_API_KEY         — IBM Cloud API key
        WATSONX_URL         — WatsonX.ai service base URL
        WATSONX_PROJECT_ID  — WatsonX project ID

    Token caching: an IAM bearer token is fetched on first use and reused
    until it is within 60 seconds of its reported expiry.
    """

    def __init__(self):
        load_dotenv()
        self.api_key = os.environ.get("IBM_API_KEY", "")
        self.url = (os.environ.get("WATSONX_URL", "")).rstrip("/")
        self.project_id = os.environ.get("WATSONX_PROJECT_ID", "")

        # Token cache: {"token": str, "expires_at": float (unix seconds)}
        self._token_cache: dict = {}

    # ------------------------------------------------------------------
    # IAM authentication
    # ------------------------------------------------------------------

    def get_iam_token(self) -> str:
        """Return a valid IAM bearer token, refreshing it when necessary."""
        now = time.time()
        cached = self._token_cache
        # Use cached token if it is still valid with a 60-second safety margin
        if cached.get("token") and cached.get("expires_at", 0) - 60 > now:
            return cached["token"]

        response = requests.post(
            _IAM_TOKEN_URL,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": self.api_key,
            },
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()

        token = payload["access_token"]
        # IBM IAM tokens expire in 3600 s; honour the field when present
        expires_in = payload.get("expires_in", 3600)
        self._token_cache = {
            "token": token,
            "expires_at": now + expires_in,
        }
        return token

    # ------------------------------------------------------------------
    # Internal helper
    # ------------------------------------------------------------------

    def _generate(self, prompt: str, max_new_tokens: int = 300) -> str:
        """
        Call the watsonx.ai text-generation endpoint and return the
        generated text.  Raises on HTTP errors so callers can fall back.
        """
        token = self.get_iam_token()
        endpoint = f"{self.url}/ml/v1/text/generation?version={_WATSONX_API_VERSION}"

        body = {
            "model_id": _MODEL_ID,
            "project_id": self.project_id,
            "input": prompt,
            "parameters": {
                "decoding_method": "greedy",
                "max_new_tokens": max_new_tokens,
                "repetition_penalty": 1.1,
            },
        }

        response = requests.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json=body,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        # Standard watsonx.ai response shape: {"results": [{"generated_text": "..."}]}
        return data["results"][0]["generated_text"].strip()

    # ------------------------------------------------------------------
    # Public high-level methods
    # ------------------------------------------------------------------

    def generate_risk_assessment(
        self, disruption_context: dict, historical_context: str | None = None
    ) -> str:
        """
        Analyse a supply-chain disruption and return a 2-3 sentence risk
        assessment string.

        Args:
            disruption_context: Arbitrary dict describing the disruption event.
            historical_context: Optional string summarising past disruptions for
                this supplier, used to improve the model's assessment.

        Returns:
            Risk assessment text (from the model, or a fallback template).
        """
        history_section = (
            f"\nHistorical record for this supplier: {historical_context}"
            if historical_context else ""
        )
        prompt = (
            "You are a risk analyst for a water utility company. "
            "Given the following supply chain disruption, provide a concise "
            "2-3 sentence risk assessment covering likelihood of impact, "
            "severity, and immediate concern.\n\n"
            f"Disruption details: {disruption_context}"
            f"{history_section}\n\n"
            "Risk assessment:"
        )
        try:
            return self._generate(prompt, max_new_tokens=200)
        except Exception as exc:
            logger.warning("generate_risk_assessment failed (%s); using fallback.", exc)
            return self.fallback_response(str(disruption_context))

    def generate_executive_summary(
        self, action_plan: dict, historical_context: str | None = None
    ) -> str:
        """
        Generate a one-paragraph executive summary of an action plan,
        suitable for the Director of Operations.

        Args:
            action_plan: Dict containing the recommended response actions.
            historical_context: Optional string summarising past disruptions,
                included to give the model supplier-specific context.

        Returns:
            Executive summary text (from the model, or a fallback template).
        """
        history_section = (
            f"\nSupplier history: {historical_context}"
            if historical_context else ""
        )
        prompt = (
            "You are a senior operations advisor at a water utility. "
            "Write a single, concise paragraph (executive summary) of the "
            "following action plan for the Director of Operations. "
            "Use professional, decision-ready language.\n\n"
            f"Action plan: {action_plan}"
            f"{history_section}\n\n"
            "Executive summary:"
        )
        try:
            return self._generate(prompt, max_new_tokens=250)
        except Exception as exc:
            logger.warning("generate_executive_summary failed (%s); using fallback.", exc)
            return self.fallback_response(str(action_plan))

    def fallback_response(self, context: str) -> str:
        """
        Template-based response used when the watsonx.ai API is unavailable,
        ensuring the demo continues to function end-to-end.

        Args:
            context: A string description of the disruption or action plan.

        Returns:
            A pre-built, human-readable response string.
        """
        return (
            "⚠️  [Offline mode — WatsonX API unavailable]\n\n"
            "A supply chain disruption has been detected that may affect water "
            "treatment chemical availability or critical equipment delivery. "
            "Recommended immediate actions: (1) activate the emergency supplier "
            "roster, (2) assess current inventory buffers against 30-day demand, "
            "and (3) escalate to the Director of Operations for authorisation of "
            "expedited procurement. Continuous monitoring is advised until supply "
            "is restored to normal levels.\n\n"
            f"Context snapshot: {context[:300]}"
        )
