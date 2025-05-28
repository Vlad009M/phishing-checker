import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
import os
import joblib

# Завантаження навчального набору з CSV
DATA_PATH = os.path.join(os.path.dirname(__file__), 'emails.csv')

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError("Файл emails.csv не знайдено")

data = pd.read_csv(DATA_PATH)

# Очистка даних
if 'text' not in data.columns or 'label' not in data.columns:
    raise ValueError("CSV-файл має містити колонки 'text' та 'label'")

texts = data['text'].astype(str).tolist()
labels = data['label'].astype(int).tolist()

# Побудова моделі
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)
model = LogisticRegression(max_iter=1000)
model.fit(X, labels)

# Аналіз тексту

def analyze_with_local_ai(text):
    if not text.strip():
        return "Текст порожній або некоректний."

    x = vectorizer.transform([text])
    proba = model.predict_proba(x)[0][1]
    label = model.predict(x)[0]

    if label == 1:
        return f"⚠️ Текст має ознаки фішингу (ймовірність {round(proba * 100, 2)}%)"
    else:
        return f"✅ Текст виглядає безпечним (ймовірність {round((1 - proba) * 100, 2)}%)"
