"""AP forecast: predicted payment delay, a rule-based vendor risk level and an LLM explanation request."""
from .predict import predict_delay_days
from .explain import build_explanation_request
from .risk import vendor_risk

__version__ = "0.10.0"
__all__ = ["predict_delay_days", "build_explanation_request", "vendor_risk"]
