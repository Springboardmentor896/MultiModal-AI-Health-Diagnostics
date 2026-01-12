import json
import os

# Load parameter ranges
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
RANGE_FILE = os.path.join(BASE_DIR, "data", "parameter_ranges.json")

with open(RANGE_FILE) as f:
    PARAM_RANGES = json.load(f)


def classify(parameter, value, sex):
    """
    Classifies a single blood parameter value as low, normal, or high
    """

    if value is None:
        return {"status": "missing", "value": value}

    if parameter not in PARAM_RANGES:
        return {"status": "unknown2", "value": value}

    ranges = PARAM_RANGES[parameter]

    # Handle sex-specific ranges
    if isinstance(ranges, dict):
        low, high = ranges.get(sex, ranges.get("default", [None, None]))
    else:
        low, high = ranges

    if low is None or high is None:
        status = "unknown1"
    elif value < low:
        status = "low"
    elif value > high:
        status = "high"
    else:
        status = "normal"

    return {
        "value": value,
        "status": status,
        "range": [low, high]
    }


def interpret_parameters(params, sex):
    """
    Interprets all extracted parameters
    """
    results = {}

    for param, value in params.items():
        results[param] = classify(param, value, sex)

    return results
