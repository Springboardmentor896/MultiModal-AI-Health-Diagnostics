from processing_04.deviation_calculator import calculate_deviation
from processing_04.probability_mapper import to_probability
from processing_04.confidence_mapper import confidence_band
import json

def load_rules():
    with open("config_02/disease_rules.json") as f:
        return json.load(f)

def assess_disease_risks(parameters, parameter_status, deviations):
    """
    parameters: raw numeric values
    parameter_status: Low / Normal / High
    deviations: percentage deviation from normal
    """


    rules = load_rules()
    disease_results = {}

    for disease, rule in rules.items():
        total_deviation = 0
        reasons = []

        for param, expected_status in rule["conditions"].items():
            if param in parameter_status and parameter_status[param] == expected_status:
                deviation = calculate_deviation(param, parameter_values[param])
                total_deviation += deviation

                reasons.append(
                    f"{param.upper()} is {expected_status} "
                    f"(deviation {round(deviation,2)}%)"
                )

        if total_deviation > 0:
            probability = to_probability(total_deviation)
            band = confidence_band(probability)

            disease_results[disease] = {
                "probability": probability,
                "risk_level": band,
                "explanation": reasons
            }

    return disease_results
