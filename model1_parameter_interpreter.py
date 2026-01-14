def classify(param, value, ranges):
    """
    Classify parameter value as Normal, Low, or High
    
    Args:
        param: parameter name
        value: parameter value
        ranges: dictionary with 'low' and 'high' thresholds
    
    Returns:
        str: 'Normal', 'Low', or 'High'
    """
    if param not in ranges:
        return "Unknown"
    
    low = ranges[param]['low']
    high = ranges[param]['high']
    
    if value < low:
        return "Low"
    elif value > high:
        return "High"
    else:
        return "Normal"