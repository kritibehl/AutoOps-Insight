import pickle

# Load the trained model and vectorizer
with open("ml_model/log_model.pkl", "rb") as f:
    vectorizer, model = pickle.load(f)

def predict_log_issue(log_text: str):
    X = vectorizer.transform([log_text])
    prediction = model.predict(X)[0]
    proba = model.predict_proba(X).max()
    return {
        "predicted_issue": prediction,
        "confidence": round(proba, 2)
    }
