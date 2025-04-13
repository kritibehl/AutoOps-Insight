import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pickle

# Load and process data
df = pd.read_csv("log_train.csv")
X = df["log_text"]
y = df["label"]

# Vectorize text logs
vectorizer = TfidfVectorizer()
X_vec = vectorizer.fit_transform(X)

# Train model
model = LogisticRegression()
model.fit(X_vec, y)

# Save model + vectorizer
with open("log_model.pkl", "wb") as f:
    pickle.dump((vectorizer, model), f)

print("✅ Model trained and saved as log_model.pkl")
