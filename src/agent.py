# =============================================================================
# AquaShield — Supply Chain Disruption Response Agent
# File: src/agent.py
#
# Purpose:
#   Orchestrates disruption-response logic. Receives a disruption event,
#   queries WatsonX for recommendations, and returns a full action plan.
# =============================================================================

import json
import logging
import os
import time
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# Chemicals that directly affect drinking water safety
_HEALTH_CRITICAL_CHEMICALS = {"Liquid Chlorine", "Sodium Fluoride"}


def _load_json(filename: str) -> list:
    path = os.path.join(_DATA_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logger.warning("Could not load %s: %s", filename, exc)
        return []


def _score_criticality(supplier: dict, delay_days: int) -> dict:
    """
    Derive a criticality level from supplier category and stock vs delay.
    Returns {"level": str, "reason": str}.
    """
    category = supplier.get("category", "")
    stock_days = supplier.get("current_stock_days") or 0
    chemical = supplier.get("chemical_type", "") or ""

    if category == "CRITICAL_CHEMICAL":
        if delay_days >= stock_days:
            level = "CRITICAL"
            reason = (
                f"Delay of {delay_days} days meets or exceeds current stock of "
                f"{stock_days} days. Immediate action required to prevent treatment interruption."
            )
        elif delay_days >= stock_days * 0.6:
            level = "HIGH"
            reason = (
                f"Delay of {delay_days} days will consume {round(delay_days/stock_days*100)}% "
                f"of the {stock_days}-day stock buffer. Expedite backup sourcing."
            )
        else:
            level = "MEDIUM"
            reason = (
                f"Current stock of {stock_days} days provides adequate buffer. "
                f"Monitor and place backup order within 48 hours."
            )
    elif category == "TREATMENT_CHEMICAL":
        level = "HIGH" if delay_days > 14 else "MEDIUM"
        reason = (
            f"{chemical} delay of {delay_days} days impacts treatment schedule. "
            f"{'Activate backup supplier immediately.' if delay_days > 14 else 'Monitor closely.'}"
        )
    else:
        level = "LOW" if delay_days <= 14 else "MEDIUM"
        reason = f"Non-chemical equipment delay of {delay_days} days. Assess maintenance schedule impact."

    return {"level": level, "reason": reason}


class AquaShieldAgent:
    """
    Agent that analyses supply-chain disruptions and proposes response plans
    using IBM WatsonX foundation models.
    """

    def __init__(self, watsonx_client):
        self.client = watsonx_client

    def analyse(self, disruption: dict) -> dict:
        """Analyse a disruption event and return a recommended action plan."""
        start = time.perf_counter()

        supplier_id = disruption.get("supplier_id", "").upper()
        description = disruption.get("description", "")
        delay_days = int(disruption.get("delay_days", 0))

        # ── Load data ──────────────────────────────────────────────────────
        suppliers = _load_json("suppliers.json")
        orders = _load_json("orders.json")
        disruptions = _load_json("disruptions.json")

        supplier_map = {s["id"]: s for s in suppliers}

        # ── Find affected supplier ─────────────────────────────────────────
        supplier = supplier_map.get(supplier_id, {
            "id": supplier_id, "name": supplier_id,
            "chemical_type": "Unknown", "category": "UNKNOWN",
            "criticality": "MEDIUM", "current_stock_days": 0,
            "backup_supplier_ids": [], "is_backup": False
        })

        # ── Affected orders ────────────────────────────────────────────────
        affected_orders = [
            o for o in orders if o.get("supplier_id") == supplier_id
        ]

        # ── Alternative suppliers ──────────────────────────────────────────
        backup_ids = supplier.get("backup_supplier_ids", [])
        alternatives = [supplier_map[bid] for bid in backup_ids if bid in supplier_map]

        # Also surface same-chemical backups not already listed
        chem = supplier.get("chemical_type")
        if chem:
            for s in suppliers:
                if s["is_backup"] and s.get("chemical_type") == chem and s["id"] not in backup_ids:
                    alternatives.append(s)

        # Sort by reliability score descending
        alternatives.sort(key=lambda s: s.get("reliability_score", 0), reverse=True)

        # ── Criticality assessment ─────────────────────────────────────────
        criticality = _score_criticality(supplier, delay_days)

        # ── Health risk flag ───────────────────────────────────────────────
        chemical_type = supplier.get("chemical_type") or ""
        stock_days = supplier.get("current_stock_days") or 0
        days_until_stockout = max(0, stock_days - delay_days)
        health_risk_warning = None
        if chemical_type in _HEALTH_CRITICAL_CHEMICALS:
            health_risk_warning = (
                f"⚠️ PUBLIC HEALTH ALERT: {chemical_type} is essential for safe drinking water. "
                f"{'Stock will be DEPLETED before supply resumes — EPA Safe Drinking Water Act compliance at risk. Escalate to Director of Operations IMMEDIATELY.' if days_until_stockout <= 0 else f'Stock covers approximately {days_until_stockout} more days. Activate backup supplier within 24 hours to avoid compliance risk.'}"
            )

        # ── Historical context ─────────────────────────────────────────────
        past = [d for d in disruptions if d.get("supplier_id") == supplier_id]
        historical_context = None
        if past:
            avg_days = round(sum(d.get("actual_delay_days", 0) for d in past) / len(past))
            historical_context = (
                f"{supplier.get('name', supplier_id)} has had {len(past)} recorded disruption(s) "
                f"in the past 12 months with an average delay of {avg_days} days. "
                f"Previous resolution: {past[-1].get('resolution', 'N/A')}"
            )

        # ── Action plan ────────────────────────────────────────────────────
        top_alt = alternatives[0] if alternatives else None
        immediate_actions = []
        if criticality["level"] in ("CRITICAL", "HIGH"):
            immediate_actions.append(
                f"Contact {top_alt['name']} ({top_alt['contact_name']}, {top_alt['contact_phone']}) to place emergency order immediately."
                if top_alt else "Identify and contact an emergency backup supplier immediately."
            )
            immediate_actions.append(f"Audit current {chemical_type or 'inventory'} stock levels across all treatment plants.")
            immediate_actions.append("Notify Director of Operations and activate the supply chain contingency protocol.")
        if health_risk_warning:
            immediate_actions.append("File incident report with compliance team — EPA notification may be required if stock drops below 5 days.")
        immediate_actions.append(f"Request daily status updates from {supplier.get('name', supplier_id)} until supply is restored.")
        if len(affected_orders) > 0:
            immediate_actions.append(f"Place replacement orders for {len(affected_orders)} affected PO(s) via backup supplier within 24 hours.")

        action_plan = {
            "immediate_actions": immediate_actions,
            "recommended_supplier": top_alt["name"] if top_alt else "No vetted backup on file — source manually.",
            "recommended_supplier_id": top_alt["id"] if top_alt else None,
            "recommended_supplier_contact": top_alt.get("contact_email") if top_alt else None,
        }

        # ── AI-generated narrative ─────────────────────────────────────────
        context_for_ai = {
            "supplier_id": supplier_id,
            "supplier_name": supplier.get("name"),
            "chemical_type": chemical_type,
            "delay_days": delay_days,
            "description": description,
            "current_stock_days": supplier.get("current_stock_days"),
            "affected_orders_count": len(affected_orders),
            "criticality_level": criticality["level"],
        }
        ai_risk_assessment = self.client.generate_risk_assessment(
            context_for_ai, historical_context=historical_context
        )

        plan_for_summary = {
            "supplier": supplier.get("name"),
            "criticality": criticality["level"],
            "affected_orders": len(affected_orders),
            "recommended_action": action_plan["immediate_actions"][0] if action_plan["immediate_actions"] else "",
            "alternative_supplier": action_plan["recommended_supplier"],
        }
        executive_summary = self.client.generate_executive_summary(
            plan_for_summary, historical_context=historical_context
        )

        # ── Build response ─────────────────────────────────────────────────
        execution_time = round(time.perf_counter() - start, 2)
        time_saved_estimate = "~3 hours manual → {:.1f} seconds AI".format(execution_time)

        result = {
            "supplier": {
                "id": supplier_id,
                "name": supplier.get("name"),
                "chemical_type": chemical_type or None,
                "category": supplier.get("category"),
            },
            "disruption": {
                "description": description,
                "delay_days": delay_days,
            },
            "criticality_assessment": criticality,
            "affected_orders": affected_orders,
            "alternatives": [
                {
                    "id": a["id"],
                    "name": a["name"],
                    "reliability_score": a.get("reliability_score"),
                    "lead_time_days": a.get("lead_time_days"),
                    "contact_name": a.get("contact_name"),
                    "contact_phone": a.get("contact_phone"),
                    "contact_email": a.get("contact_email"),
                }
                for a in alternatives
            ],
            "action_plan": action_plan,
            "health_risk_warning": health_risk_warning,
            "historical_context": historical_context,
            "ai_risk_assessment": ai_risk_assessment,
            "executive_summary": executive_summary,
            "days_until_stockout": days_until_stockout,
            "time_saved_estimate": time_saved_estimate,
            "execution_time_seconds": execution_time,
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(
            "Disruption analysis complete: supplier=%s criticality=%s affected_orders=%d time=%.2fs",
            supplier_id, criticality["level"], len(affected_orders), execution_time
        )
        return result
