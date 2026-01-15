def classify(param, value, ranges):
   
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