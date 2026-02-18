

def assess_risks_from_model1(classification_results, age=None, gender=None):
    
    identified_risks = []
    risk_score = 0
    values = {}
    
    age_group = "adult"
    if age is not None:
        if age < 18:
            age_group = "pediatric"
        elif age < 30:
            age_group = "young_adult"
        elif age < 50:
            age_group = "adult"
        elif age < 65:
            age_group = "middle_aged"
        else:
            age_group = "senior"
    
    if gender:
        gender = gender.lower()
        if gender not in ['male', 'female']:
            gender = None
    
    def get_risk_desc(param_lower, risk_type, age_group, gender):

        if risk_type == 'Low':
            if param_lower == 'hemoglobin':
                if age_group == 'senior':
                    return 'Anemia risk - CRITICAL for seniors (increases fall & cognitive issues)'
                elif gender == 'female':
                    return 'Anemia risk - low hemoglobin, check for iron deficiency'
                else:
                    return 'Anemia risk - may cause fatigue and weakness'
            elif param_lower == 'hdl':
                if age_group == 'senior':
                    return 'Low protective cholesterol - HIGH CV risk in seniors'
                else:
                    return 'Low protective cholesterol - increased cardiovascular disease risk'
            elif param_lower == 'wbc':
                return 'Low white blood cell count - weakened immune system, infection risk'
            elif param_lower == 'creatinine':
                if age_group == 'young_adult':
                    return 'Low creatinine - atypical, verify kidney function'
                return 'Low creatinine - may indicate muscle loss or kidney issues'
            
        elif risk_type == 'High':
            if param_lower == 'glucose':
                if age_group == 'young_adult':
                    return 'Diabetes/Prediabetes risk - UNUSUAL in young age, immediate intervention'
                elif age_group == 'pediatric':
                    return 'High glucose - check for Type 1 Diabetes risk'
                elif age_group == 'senior':
                    return 'High glucose - common in seniors, requires management'
                else:
                    return 'Diabetes/Prediabetes risk - metabolic disorder'
            
            elif param_lower == 'cholesterol':
                if age_group == 'young_adult':
                    return 'Hypercholesterolemia - UNUSUAL in young age, investigate cause'
                elif age_group == 'senior':
                    return 'High cholesterol - increased CV risk in seniors'
                else:
                    return 'Hypercholesterolemia - cardiovascular disease risk'
            
            elif param_lower == 'creatinine':
                if age_group == 'young_adult':
                    return 'High creatinine in young adult - URGENT kidney evaluation needed'
                elif age_group == 'senior':
                    return 'High creatinine in seniors - Kidney dysfunction risk'
                else:
                    return 'Kidney dysfunction risk - impaired renal filtration'
            
            elif param_lower == 'ast':
                if age_group == 'senior':
                    return 'Elevated AST in seniors - investigate for liver disease'
                else:
                    return 'Elevated liver enzyme - liver damage, hepatitis, or muscle injury risk'
            
            elif param_lower == 'alt':
                if age_group == 'senior':
                    return 'Elevated ALT in seniors - check liver function'
                else:
                    return 'Elevated liver enzyme - possible liver damage or inflammation'
            
            elif param_lower == 'wbc':
                return 'High white blood cell count - infection, inflammation, or blood disorder'
        
        low_risk_defaults = {
            'hemoglobin': 'Anemia risk - may cause fatigue and weakness',
            'hdl': 'Low protective cholesterol - increased cardiovascular disease risk',
            'rbc': 'Low red blood cell count - anemia and oxygen delivery issues',
            'albumin': 'Low protein levels - liver or kidney dysfunction, malnutrition',
            'calcium': 'Hypocalcemia - bone health issues, muscle/nerve problems',
            'potassium': 'Hypokalemia - cardiac arrhythmia risk, muscle weakness',
            'sodium': 'Hyponatremia - fluid balance issues, neurological symptoms',
            'platelets': 'Low platelet count - bleeding disorder risk'
        }
        
        high_risk_defaults = {
            'glucose': 'Diabetes/Prediabetes risk - metabolic disorder',
            'cholesterol': 'Hypercholesterolemia - cardiovascular disease risk',
            'ldl': 'High bad cholesterol - atherosclerosis and heart disease risk',
            'triglycerides': 'Hypertriglyceridemia - cardiovascular and pancreatic risk',
            'bun': 'Elevated urea - kidney dysfunction or dehydration',
            'platelets': 'High platelet count - blood clotting disorder risk'
        }
        
        if risk_type == 'Low':
            return low_risk_defaults.get(param_lower, 'Risk detected - review with physician')
        else:
            return high_risk_defaults.get(param_lower, 'Risk detected - review with physician')
    
    for param, info in classification_results.items():
        param_lower = param.lower()
        values[param_lower] = info.get('value', 0)
        status = info.get('status', 'Normal')
        
        if status == 'Low':
            risk_desc = get_risk_desc(param_lower, 'Low', age_group, gender)
            identified_risks.append(f"Low {param} ({info.get('value')}): {risk_desc}")
            risk_score += 1
        elif status == 'High':
            risk_desc = get_risk_desc(param_lower, 'High', age_group, gender)
            identified_risks.append(f"High {param} ({info.get('value')}): {risk_desc}")
            risk_score += 1
    
    glucose = values.get('glucose', 0)
    cholesterol = values.get('cholesterol', 0)
    hemoglobin = values.get('hemoglobin', 0)
    wbc = values.get('wbc', 0)
    platelets = values.get('platelets', 0)
    hdl = values.get('hdl', 1000)
    ldl = values.get('ldl', 0)
    triglycerides = values.get('triglycerides', 0)
    alt = values.get('alt', 0)
    ast = values.get('ast', 0)
    creatinine = values.get('creatinine', 0)
    bun = values.get('bun', 0)
    
    glucose_high = classification_results.get('Glucose', {}).get('status') == 'High'
    glucose_low = classification_results.get('Glucose', {}).get('status') == 'Low'
    cholesterol_high = classification_results.get('Cholesterol', {}).get('status') == 'High'
    hemoglobin_low = classification_results.get('Hemoglobin', {}).get('status') == 'Low'
    wbc_high = classification_results.get('WBC', {}).get('status') == 'High'
    platelets_low = classification_results.get('Platelets', {}).get('status') == 'Low'
    
    if glucose_high and cholesterol_high:
        identified_risks.append("CRITICAL: High Glucose + High Cholesterol → Diabetes & Cardiovascular disease risk")
        risk_score += 2
    
    if glucose_high and hemoglobin_low:
        identified_risks.append("HIGH: High Glucose + Low Hemoglobin → Diabetes with anemia")
        risk_score += 2
    
    if wbc_high and platelets_low:
        identified_risks.append("HIGH: High WBC + Low Platelets → Infection with bleeding risk")
        risk_score += 2
    
    if wbc_high and hemoglobin_low:
        identified_risks.append("HIGH: High WBC + Low Hemoglobin → Infection with anemia")
        risk_score += 2
    
    if glucose_high:
        identified_risks.append("Elevated Glucose: Diabetes/Prediabetes risk")
        risk_score += 1
    
    if cholesterol_high:
        identified_risks.append("Elevated Cholesterol: Cardiovascular risk")
        risk_score += 1
    
    if hemoglobin_low:
        identified_risks.append("Low Hemoglobin: Anemia risk")
        risk_score += 1
    
    if wbc_high:
        identified_risks.append("High WBC: Possible infection/inflammation")
        risk_score += 1
    
    if platelets_low:
        identified_risks.append("Low Platelets: Bleeding disorder risk")
        risk_score += 1
    
    if cholesterol > 0 and hdl > 0:
        tc_hdl = cholesterol / hdl
        if tc_hdl > 5:
            identified_risks.append(f"High TC/HDL ratio ({tc_hdl:.2f}): Increased cardiovascular risk")
            risk_score += 1
    
    if ldl > 0 and hdl > 0:
        ldl_hdl = ldl / hdl
        if ldl_hdl > 3.5:
            identified_risks.append(f"High LDL/HDL ratio ({ldl_hdl:.2f}): Increased cardiovascular risk")
            risk_score += 1
    
    if risk_score >= 7:
        risk_level = "CRITICAL"
    elif risk_score >= 5:
        risk_level = "HIGH"
    elif risk_score >= 2:
        risk_level = "MODERATE"
    else:
        risk_level = "LOW"
    
    risk_multiplier = 1.0
    if age is not None:
        if age_group == 'young_adult':
            risk_multiplier = 0.8
        elif age_group == 'senior':
            risk_multiplier = 1.5
    
    adjusted_risk_score = int(risk_score * risk_multiplier)
    
    if adjusted_risk_score >= 7:
        risk_level = "CRITICAL"
    elif adjusted_risk_score >= 5:
        risk_level = "HIGH"
    elif adjusted_risk_score >= 2:
        risk_level = "MODERATE"
    else:
        risk_level = "LOW"
    
    demographic_context = {
        'age': age,
        'gender': gender,
        'age_group': age_group if age is not None else 'unknown',
        'risk_multiplier': risk_multiplier if age is not None else 'N/A'
    }
    
    return {
        'identified_risks': identified_risks if identified_risks else ["No significant risks identified"],
        'risk_score': adjusted_risk_score,
        'risk_level': risk_level,
        'demographic_context': demographic_context
    }


def _get_platelets_count(values):
    platelets = values.get("Platelets")
    if platelets is None:
        return None
    if platelets < 1000:
        return platelets * 100000
    return platelets


def identify_patterns(values):
    patterns = []

    if values.get("Glucose", 0) > 126 and values.get("Cholesterol", 0) > 240:
        patterns.append("High risk of Diabetes and Cardiovascular Disease")

    if 100 < values.get("Glucose", 0) <= 126:
        patterns.append("Prediabetes risk (glucose 100–126)")

    if values.get("Glucose", 0) > 126:
        patterns.append("Diabetes risk (glucose >126)")

    if values.get("Cholesterol", 0) > 240:
        patterns.append("Hypercholesterolemia risk (cholesterol >240)")

    if values.get("WBC", 0) > 11000 and values.get("Hemoglobin", 0) < 12:
        patterns.append("Possible Infection with Anemia")

    if values.get("WBC", 0) > 11000:
        patterns.append("Possible infection/inflammation (high WBC)")

    if 0 < values.get("WBC", 0) < 4000:
        patterns.append("Possible immunosuppression risk (low WBC)")

    if values.get("Hemoglobin", 0) < 12:
        patterns.append("Anemia risk (low hemoglobin)")

    platelets_count = _get_platelets_count(values)
    if platelets_count is not None and platelets_count < 150000:
        patterns.append("Risk of Bleeding Disorder")

    if platelets_count is not None and platelets_count > 450000:
        patterns.append("Thrombocytosis risk (high platelets)")


    if values.get("Glucose", 0) > 126 and values.get("Hemoglobin", 0) < 12:
        patterns.append("Diabetes with possible anemia (high glucose + low hemoglobin)")

    if values.get("WBC", 0) > 11000 and platelets_count is not None and platelets_count < 150000:
        patterns.append("Infection with bleeding risk (high WBC + low platelets)")

    if values.get("Cholesterol", 0) > 240 and values.get("Hemoglobin", 0) < 12:
        patterns.append("Cardio-metabolic strain (high cholesterol + low hemoglobin)")

    if values.get("LDL", 0) > 160 and values.get("HDL", 1000) < 40:
        patterns.append("High cardiovascular risk (high LDL + low HDL)")

    if values.get("LDL", 0) > 160:
        patterns.append("High LDL risk (LDL >160)")

    if values.get("HDL", 1000) < 40:
        patterns.append("Low HDL risk (HDL <40)")

    if values.get("Triglycerides", 0) > 150 and values.get("HDL", 1000) < 40:
        patterns.append("Atherogenic profile (high TG + low HDL)")

    if values.get("Triglycerides", 0) > 200:
        patterns.append("High triglycerides risk (TG >200)")

    if values.get("Glucose", 0) > 126 and values.get("Triglycerides", 0) > 150:
        patterns.append("Metabolic syndrome indicators (high glucose + high TG)")

    if values.get("Glucose", 0) > 126 and values.get("HDL", 1000) < 40:
        patterns.append("Metabolic risk (high glucose + low HDL)")

    if values.get("ALT", 0) > 40 and values.get("AST", 0) > 40:
        patterns.append("Possible liver stress (elevated ALT + AST)")

    if values.get("ALT", 0) > 40 and values.get("AST", 0) <= 40:
        patterns.append("Possible liver stress (elevated ALT)")

    if values.get("AST", 0) > 40 and values.get("ALT", 0) <= 40:
        patterns.append("Possible liver stress (elevated AST)")

    if values.get("Creatinine", 0) > 1.2 and values.get("Urea", 0) > 40:
        patterns.append("Possible kidney function impairment (high creatinine + urea)")

    if values.get("Creatinine", 0) > 1.2 and values.get("Urea", 0) <= 40:
        patterns.append("Possible kidney strain (high creatinine)")

    if values.get("Urea", 0) > 40 and values.get("Creatinine", 0) <= 1.2:
        patterns.append("Possible kidney strain (high urea)")

    tc = values.get("Cholesterol")
    hdl = values.get("HDL")
    ldl = values.get("LDL")
    tg = values.get("Triglycerides")

    if tc is not None and hdl:
        tc_hdl = tc / hdl
        if tc_hdl > 5:
            patterns.append("High cardiovascular risk (TC/HDL ratio > 5)")

    if ldl is not None and hdl:
        ldl_hdl = ldl / hdl
        if ldl_hdl > 3.5:
            patterns.append("High cardiovascular risk (LDL/HDL ratio > 3.5)")

    if tg is not None and hdl:
        tg_hdl = tg / hdl
        if tg_hdl > 4:
            patterns.append("Insulin resistance risk (TG/HDL ratio > 4)")

    return patterns


def calculate_risk_score(values):
    score = 0

    if values.get("Glucose", 0) > 126:
        score += 1
    if 100 < values.get("Glucose", 0) <= 126:
        score += 1
    if values.get("Cholesterol", 0) > 240:
        score += 1
    if values.get("WBC", 0) > 11000:
        score += 1
    if 0 < values.get("WBC", 0) < 4000:
        score += 1
    platelets_count = _get_platelets_count(values)
    if platelets_count is not None and platelets_count < 150000:
        score += 1
    if platelets_count is not None and platelets_count > 450000:
        score += 1
    if values.get("Hemoglobin", 0) < 12:
        score += 1
    if values.get("LDL", 0) > 160:
        score += 1
    if values.get("HDL", 1000) < 40:
        score += 1
    if values.get("Triglycerides", 0) > 200:
        score += 1
    if values.get("ALT", 0) > 40 or values.get("AST", 0) > 40:
        score += 1
    if values.get("Creatinine", 0) > 1.2 or values.get("Urea", 0) > 40:
        score += 1
    if values.get("LDL", 0) > 160 and values.get("HDL", 1000) < 40:
        score += 1
    if values.get("Triglycerides", 0) > 150 and values.get("HDL", 1000) < 40:
        score += 1
    if values.get("Glucose", 0) > 126 and values.get("Triglycerides", 0) > 150:
        score += 1
    if values.get("WBC", 0) > 11000 and values.get("Hemoglobin", 0) < 12:
        score += 1
    if values.get("Cholesterol", 0) > 240 and values.get("Glucose", 0) > 126:
        score += 1

    tc = values.get("Cholesterol")
    hdl = values.get("HDL")
    ldl = values.get("LDL")
    tg = values.get("Triglycerides")

    if tc is not None and hdl and (tc / hdl) > 5:
        score += 1
    if ldl is not None and hdl and (ldl / hdl) > 3.5:
        score += 1
    if tg is not None and hdl and (tg / hdl) > 4:
        score += 1

    return score
