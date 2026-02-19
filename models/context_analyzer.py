class ContextAnalyzer:
    def __init__(self):
        self.PEDIATRIC_CUTOFF = 18
        self.GERIATRIC_CUTOFF = 65
        
    def refine_analysis(self, analyzed_data, patient_age=None, patient_gender=None, is_pregnant=False):
        refined_data = []
        
        try:
            age = int(patient_age) if patient_age else None
        except:
            age = None
            
        gender = patient_gender.lower() if patient_gender else ""

        for item in analyzed_data:
            param = item.get('Standard_Name', '')
            val = item.get('Value')
            flag = item.get('Flag', '')
            simple_flag = flag.split(' (')[0] if flag else ""
            status = item.get('Status', 'Normal')
            
            context_note = ""

            # 1. PEDIATRIC CONTEXT (Age < 18)
            if age and age < self.PEDIATRIC_CUTOFF:
                
                if param == "Alkaline Phosphatase" and simple_flag == "High":
                    context_note = "Elevated ALP is physiological in growing children (active bone turnover)."
                    status = "Normal (Context)"

                if param == "Lymphocytes" and simple_flag == "High":
                    context_note = "Lymphocyte counts are naturally higher in children than adults."
                    status = "Normal (Context)"
                
                if param == "Creatinine" and simple_flag == "Low":
                    context_note = "Low creatinine is expected in children due to lower muscle mass."
                    status = "Normal (Context)"

            # 2. GERIATRIC CONTEXT (Age > 65)
            elif age and age > self.GERIATRIC_CUTOFF:
                
                if param == "ESR" and simple_flag == "High":
                    context_note = "Mildly elevated ESR is common with advancing age."
                    status = "Normal (Context)"
                
                if param == "Creatinine" and simple_flag == "High":
                     context_note = "Suggest calculating eGFR; creatinine alone may underestimate renal decline in elderly."

            # 3. GENDER & PREGNANCY CONTEXT
            if gender.startswith('f'):
                
                # --- PREGNANCY SPECIFIC ---
                if is_pregnant:
                    if param == "Hemoglobin" and simple_flag == "Low":
                        context_note = "Dilutional anemia is expected during pregnancy."
                        status = "Normal (Context)"
                    
                    if param == "Total WBC" and simple_flag == "High":
                        context_note = "Leukocytosis (High WBC) is physiological during pregnancy."
                        status = "Normal (Context)"

                    if param == "Alkaline Phosphatase" and simple_flag == "High":
                        context_note = "ALP rises during pregnancy (placental origin)."
                        status = "Normal (Context)"
                
                # --- GENERAL FEMALE ---
                elif not is_pregnant:
                    if param == "Hemoglobin" and simple_flag == "Low" and val >= 11.5:
                        context_note = "Borderline for adult females (consider menstruation)."
                        status = "Normal (Context)"
                    
                    if param == "Uric Acid" and simple_flag == "High":
                        context_note = "Verify menopausal status; uric acid rises post-menopause."

            if gender.startswith('m'):
                if param == "Creatinine" and simple_flag == "High" and val < 1.4:
                     context_note = "Higher creatinine often seen in males with high muscle mass."
                     status = "Normal (Context)"

            item['Context_Note'] = context_note.strip()
            item['Status'] = status
            refined_data.append(item)
            
        return refined_data
