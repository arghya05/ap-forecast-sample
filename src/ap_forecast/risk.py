"""Rule-based vendor payment-risk level from the predicted delay (STORY-03). No LLM, no network, no config read.

The rule is a fixed, auditable threshold check on predict_delay_days, so every level can be traced to the vendor's
delay history. This module imports only predict, never explain, so the rule cannot reach the LLM request path.
"""
from typing import Iterable

from .predict import predict_delay_days

# Thresholds in days on the rounded prediction; strict '>' so exactly 30 is 'medium' and exactly 10 is 'low'.
HIGH_ABOVE_DAYS = 30
MEDIUM_ABOVE_DAYS = 10


def vendor_risk(history: Iterable[int]) -> str:
    """'high' if the predicted delay is above HIGH_ABOVE_DAYS, 'medium' if above MEDIUM_ABOVE_DAYS, else 'low'.

    history is one vendor's delay days (ap_pipeline delays_by_vendor value). An empty history and early payments
    only (negative delays, counted as 0 by predict_delay_days) both give 'low'.
    """
    # Predict once and keep the result: a generator history is consumed on the first pass.
    days = predict_delay_days(history)
    if days > HIGH_ABOVE_DAYS:
        return "high"
    if days > MEDIUM_ABOVE_DAYS:
        return "medium"
    return "low"
