import json
import os

# 🔹 Resolve project root dynamically
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RANGE_PATH = os.path.join(
    BASE_DIR,
    "config_02",
    "parameter_ranges.json"
)

with open(RANGE_PATH, "r") as f:
    PARAMETER_RANGES = json.load(f)


def calculate_deviation(parameters, context=None):
    """
    Calculates deviation percentage from normal range.

    Formula:
    - If value < low:
        ((low - value) / low) * 100
    - If value > high:
        ((value - high) / high) * 100
    - Else:
        0
    """

    deviations = {}

    for param, value in parameters.items():
        if param not in PARAMETER_RANGES:
            continue

        low = PARAMETER_RANGES[param]["low"]
        high = PARAMETER_RANGES[param]["high"]

        if value < low:
            deviation = ((low - value) / low) * 100
        elif value > high:
            deviation = ((value - high) / high) * 100
        else:
            deviation = 0.0

        deviations[param] = round(deviation, 2)

    return deviations
