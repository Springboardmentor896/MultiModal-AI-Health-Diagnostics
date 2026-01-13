def interpret_parameters(values, classification):
    interpretation = {}

    for parameters, status in classification.items():
        if status == "High":
            interpretation[parameters] = f"{parameters} is above the normal range."
        elif status == "Low":
            interpretation[parameters] = f"{parameters} is below the normal range."
        elif status == "Normal":
            interpretation[parameters] = f"{parameters} is within the normal range."
        else:
            interpretation[parameters] = f"{parameters} could not be classified."

    return interpretation
