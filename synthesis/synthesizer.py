def synthesize(m1, risk, context_flags):
    
    abnormal = [k for k, v in m1.items() if v["status"] != "Normal"]

    return {
        "abnormal_parameters": abnormal,
        "risk_level": risk[0],           
        "risk_probability": round(risk[1], 2),
        "context_notes": context_flags 
    }