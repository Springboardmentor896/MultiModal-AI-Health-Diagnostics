import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(BASE_DIR, "config_02", "contextual_ranges.json")) as f:
    CONTEXT_RANGES = json.load(f)


def get_contextual_range(parameter, context):
    """
    Selects the correct (low, high) range based on patient context
    """

    param_ranges = CONTEXT_RANGES.get(parameter)

    if not param_ranges:
        return None, None

    # Priority 1: pregnancy
    if context.get("pregnant") and "pregnant" in param_ranges:
        r = param_ranges["pregnant"]
        return r["low"], r["high"]

    # Priority 2: gender
    gender = context.get("gender")
    if gender in param_ranges:
        r = param_ranges[gender]
        return r["low"], r["high"]

    # Fallback: default
    r = param_ranges["default"]
    return r["low"], r["high"]
