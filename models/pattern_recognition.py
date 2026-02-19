class PatternRecognizer:
    def __init__(self):
        self.rules = [
            # --- ANEMIA PATTERNS ---
            {
                "condition": "Microcytic Anemia (Iron Deficiency Risk)",
                "risk_level": "High",
                "logic": lambda p: p.get('Hemoglobin') == 'Low' and p.get('MCV') == 'Low'
            },
            {
                "condition": "Macrocytic Anemia (B12/Folate Deficiency Risk)",
                "risk_level": "High",
                "logic": lambda p: p.get('Hemoglobin') == 'Low' and p.get('MCV') == 'High'
            },
            {
                "condition": "Anemia of Chronic Disease",
                "risk_level": "Medium",
                "logic": lambda p: p.get('Hemoglobin') == 'Low' and p.get('MCV') == 'Within Limits'
            },
            
            # --- INFECTION PATTERNS ---
            {
                "condition": "Acute Bacterial Infection",
                "risk_level": "High",
                "logic": lambda p: p.get('Total WBC') == 'High' and p.get('Neutrophils') == 'High'
            },
            {
                "condition": "Viral Infection Pattern",
                "risk_level": "Medium",
                "logic": lambda p: (p.get('Lymphocytes') == 'High' or p.get('Total WBC') == 'Low')
            },
            {
                "condition": "Dengue Fever Indicators",
                "risk_level": "Critical",
                "logic": lambda p: p.get('Platelet Count') == 'Low' and p.get('Total WBC') == 'Low' and p.get('PCV') == 'High'
            },

            # --- METABOLIC & ORGAN PATTERNS ---
            {
                "condition": "Hyperglycemia (Diabetes Mellitus Risk)",
                "risk_level": "High",
                "logic": lambda p: p.get('Glucose') == 'High'
            },
            {
                "condition": "Renal Failure / Insufficiency",
                "risk_level": "Critical",
                "logic": lambda p: p.get('Creatinine') == 'High' and p.get('Blood Urea') == 'High'
            },
            {
                "condition": "Liver Dysfunction (Hepatocellular)",
                "risk_level": "High",
                "logic": lambda p: (p.get('SGOT (AST)') == 'High' or p.get('SGPT (ALT)') == 'High')
            },
            {
                "condition": "Obstructive Jaundice",
                "risk_level": "High",
                "logic": lambda p: p.get('Total Bilirubin') == 'High' and p.get('Alkaline Phosphatase') == 'High'
            },
            
            # --- CARDIOVASCULAR (New) ---
            {
                "condition": "Dyslipidemia (High Cholesterol Risk)",
                "risk_level": "High",
                "logic": lambda p: p.get('Total Cholesterol') == 'High' or p.get('LDL Cholesterol') == 'High'
            }
        ]

    def _create_status_map(self, analyzed_data):
        status_map = {}
        for item in analyzed_data:
            name = item.get('Standard_Name')
            flag = item.get('Flag', '')
            simple_flag = flag.split(' (')[0]
            if name:
                status_map[name] = simple_flag
        return status_map

    def evaluate_risks(self, analyzed_data):
        status_map = self._create_status_map(analyzed_data)
        detected_patterns = []
        for rule in self.rules:
            try:
                if rule['logic'](status_map):
                    detected_patterns.append({
                        "Condition": rule['condition'],
                        "Risk": rule['risk_level']
                    })
            except:
                continue
        return detected_patterns
