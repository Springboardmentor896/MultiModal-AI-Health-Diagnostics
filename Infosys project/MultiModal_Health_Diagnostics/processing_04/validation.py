def validate_parameters(params):
    validated = {}
    for k, v in params.items():
        if v is not None and 0 < v < 1000000:
            validated[k] = v
    return validated
