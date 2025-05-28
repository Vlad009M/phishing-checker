import joblib
import os

# Завантажуємо модель (разом із TfidfVectorizer)
model_path = os.path.join(os.path.dirname(__file__), 'phishing_model.pkl')
model = joblib.load(model_path)

def predict_phishing(text):
    if not text.strip():
        return 0.0
    # Оскільки model — це Pipeline, вона сама векторизує
    proba = model.predict_proba([text])[0][1]
    return round(proba * 100, 2)
