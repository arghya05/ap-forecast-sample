"""Build the LLM request that explains a prediction to the AP user. The provider and model come from models.json."""
import json
from pathlib import Path

CONFIG = Path(__file__).with_name("models.json")


def load_config():
    return json.loads(CONFIG.read_text())


def build_explanation_request(vendor: str, predicted_days: int, config=None, risk=None) -> dict:
    """Request dict for the configured provider. risk (STORY-04) is optional and last, so existing calls are unchanged.

    When risk is not None the prompt ends with ' Risk level: <risk>.'; otherwise the request is exactly as before.
    Provider, model and max_tokens always come from config or models.json.
    """
    cfg = config or load_config()
    prompt = f"Explain in one sentence why vendor {vendor} is predicted to be paid {predicted_days} days late."
    if risk is not None:
        prompt += f" Risk level: {risk}."
    return {"provider": cfg["provider"], "model": cfg["model"], "max_tokens": cfg["max_tokens"],
            "messages": [{"role": "user", "content": prompt}]}
