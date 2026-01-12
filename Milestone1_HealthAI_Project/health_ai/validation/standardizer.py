
def standardize(data):
    return {k:v for k,v in data.items() if isinstance(v,(int,float))}
