MEDICAL_GUIDELINES = {
    "High Glucose": "Focus on low-glycemic foods, limit refined sugars, and increase aerobic exercise (30 mins/day).",
    "Low Glucose": "Ensure regular meal timing; carry a fast-acting carb source; consult a doctor regarding hypoglycemia.",
    "High LDL": "Reduce saturated and trans fats; increase soluble fiber (oats, beans); consider Omega-3 supplements.",
    "High Cholesterol": "Adopt a Mediterranean-style diet; limit high-cholesterol foods like red meat and full-fat dairy.",
    "Low HDL": "Increase healthy fats (olive oil, nuts) and incorporate strength training to boost 'good' cholesterol.",
    "High Triglycerides": "Limit alcohol and sugary beverages; reduce overall carbohydrate intake.",
    "Low Hemoglobin": "Increase iron-rich foods (lean meats, spinach) paired with Vitamin C; monitor for fatigue.",
    "High WBC": "May indicate inflammation or infection; prioritize rest, hydration, and monitor for fever.",
    "Low Platelets": "Avoid activities with high bruising risk; limit NSAIDs like aspirin unless prescribed.",
    "Low RBC": "Focus on Vitamin B12 and Folate intake (leafy greens, eggs) to support red cell production.",
    "High TSH": "Suggests underactive thyroid; ensure adequate iodine/selenium intake; consult for possible medication.",
    "Low TSH": "Suggests overactive thyroid; limit caffeine and stimulants; monitor heart rate and anxiety levels.",
    "High Creatinine": "Primary indicator of kidney stress; prioritize hydration (2L+ water) and limit excessive protein.",
    "High Bilirubin": "Support liver health by avoiding alcohol and processed sugars; monitor for yellowing of eyes/skin."
}

def retrieve_guideline(condition):
    return MEDICAL_GUIDELINES.get(condition, "")