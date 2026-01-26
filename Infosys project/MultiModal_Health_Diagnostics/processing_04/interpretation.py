from processing_04.range_selector import get_contextual_range

def interpret_with_context(parameters, context):
    status = {}

    for param, value in parameters.items():
        low, high = get_contextual_range(param, context)

        if low is None:
            continue

        if value < low:
            status[param] = "Low"
        elif value > high:
            status[param] = "High"
        else:
            status[param] = "Normal"

    return status
