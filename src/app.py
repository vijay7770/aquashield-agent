# =============================================================================
# AquaShield — Supply Chain Disruption Response Agent
# File: src/app.py
#
# Purpose:
#   Flask entry point for the AquaShield backend API.
#
# Endpoints:
#   POST /api/disruption  — analyse a supply-chain disruption event
#   GET  /api/suppliers   — list all known suppliers
#   GET  /api/orders      — list all open orders
#   GET  /api/status      — health-check / liveness probe
# =============================================================================

import json
import logging
import os

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def _load_json(filename: str) -> list:
    path = os.path.join(_DATA_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logger.warning("Could not load %s: %s", filename, exc)
        return []


@app.route("/api/status", methods=["GET"])
def status():
    suppliers = _load_json("suppliers.json")
    orders = _load_json("orders.json")
    disruptions = _load_json("disruptions.json")
    return jsonify({
        "status": "ok",
        "api": "AquaShield Supply Chain API",
        "suppliers_loaded": len(suppliers),
        "orders_tracked": len(orders),
        "disruptions_on_record": len(disruptions),
        "critical_suppliers": len([s for s in suppliers if s.get("criticality") == "CRITICAL"]),
    })


@app.route("/api/suppliers", methods=["GET"])
def get_suppliers():
    return jsonify(_load_json("suppliers.json"))


@app.route("/api/orders", methods=["GET"])
def get_orders():
    return jsonify(_load_json("orders.json"))


@app.route("/api/disruption", methods=["POST"])
def disruption():
    # Import here to avoid circular issues if watsonx_client also imports app
    from agent import AquaShieldAgent
    from watsonx_client import WatsonXClient

    body = request.get_json(silent=True) or {}

    missing = [k for k in ("supplier_id", "description", "delay_days") if k not in body]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    try:
        agent = AquaShieldAgent(WatsonXClient())
        result = agent.analyse(body)
        return jsonify(result)
    except Exception as exc:
        logger.exception("Disruption analysis failed")
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
