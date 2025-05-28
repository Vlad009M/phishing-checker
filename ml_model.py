import joblib
import os

# Повний шлях до моделі
model_path = os.path.join(os.path.dirname(__file__), 'phishing_model.pkl')

# 🔁 Якщо модель відсутня — запустити train_model
if not os.path.exists(model_path):
    print("⚠️ Модель не знайдено. Навчання з нуля...")
    from train_model import *  # імпортує і запустить одразу (бо в train_model все в глобальній області)
else:
    print("✅ Модель знайдено — завантажується...")

# Завантажити модель
model = joblib.load(model_path)

def predict_phishing(text):
    if not text.strip():
        return 0.0
    # Модель — це Pipeline, вона сама векторизує текст
    proba = model.predict_proba([text])[0][1]
    return round(proba * 100, 2)
