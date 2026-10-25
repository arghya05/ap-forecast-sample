# ap_forecast

Predicted payment delay, a rule-based vendor risk level and the LLM explanation request. Run CI: `/usr/bin/python3 ci.py`

| Function | What it returns |
|---|---|
| `predict_delay_days(history)` | Rounded mean of past delays in days (negative counted as 0; 0 when empty) |
| `vendor_risk(history)` | `'high'` above 30 predicted days, `'medium'` above 10, else `'low'`; fixed rule, no LLM |
| `build_explanation_request(vendor, predicted_days, config=None, risk=None)` | LLM request dict; the prompt ends with `" Risk level: <risk>."` when `risk` is given |

```python
from ap_forecast import vendor_risk, build_explanation_request

vendor_risk([31])                                    # 'high'
build_explanation_request("Synthetic Vendor A", 34, risk="high")
```

Module reference with inputs, outputs and examples: [docs/ap_forecast.md](docs/ap_forecast.md).
