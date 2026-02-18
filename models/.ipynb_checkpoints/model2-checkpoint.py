import numpy as np
import pandas as pd
import joblib
import os
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

def train_risk_model():
    np.random.seed(42)
    n = 1000
    data = pd.DataFrame({
        "hemoglobin": np.random.normal(14, 2, n),
        "wbc": np.random.normal(7000, 2000, n),
        "platelets": np.random.normal(250000, 50000, n),
        "glucose": np.random.normal(100, 30, n),
        "ldl": np.random.normal(130, 40, n),
        "hdl": np.random.normal(50, 15, n),
        "cholesterol": np.random.normal(180, 40, n),
        "triglycerides": np.random.normal(140, 50, n),
        "creatinine": np.random.normal(0.9, 0.3, n),
        "bilirubin": np.random.normal(0.6, 0.4, n),
        "tsh": np.random.normal(2.5, 1.5, n),
        "age": np.random.randint(18, 85, n)
    })

    data["Risk"] = (
        (data["glucose"] > 140) |               
        (data["ldl"] > 160) |                    
        ((data["age"] > 60) & (data["creatinine"] > 1.3)) | 
        (data["tsh"] > 5.0)                     
    ).astype(int)

    X = data.drop("Risk", axis=1)
    y = data["Risk"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
    
    if not os.path.exists("data"):
        os.makedirs("data")
        
    joblib.dump(model, "data/risk_model.pkl")
    print(" Model trained and saved to data/risk_model.pkl")



def calculate_risk(data, age):
    model_path = "data/risk_model.pkl"
    
    if not os.path.exists(model_path):
        train_risk_model()

    model = joblib.load(model_path)
    
    features = {
        "hemoglobin": 14.0, "wbc": 7000, "platelets": 250000,
        "glucose": 90, "ldl": 100, "hdl": 50, "cholesterol": 180,
        "triglycerides": 130, "creatinine": 0.9, "bilirubin": 0.5,
        "tsh": 2.0, "age": age if age else 35
    }
    for key in features:
        if key in data:
            features[key] = data[key]

    input_df = pd.DataFrame([features])
    
    prob = model.predict_proba(input_df)[0][1]
    
    if prob > 0.7:
        level = "High Risk"
    elif prob > 0.3:
        level = "Medium Risk"
    else:
        level = "Low Risk"
        
    return (level, prob * 100)


if __name__ == "__main__":
    train_risk_model()







    