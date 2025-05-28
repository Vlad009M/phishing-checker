import pandas as pd
import os
import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
import joblib

# --- Автоматичне оновлення навчального набору ---
DATA_PATH = os.path.join(os.path.dirname(__file__), 'emails.csv')

# Якщо новий текст для донавчання існує
new_data_file = os.path.join(os.path.dirname(__file__), 'new_samples.csv')
if os.path.exists(new_data_file):
    with open(new_data_file, newline='', encoding='utf-8') as nf:
        reader = csv.DictReader(nf)
        new_samples = list(reader)

    if new_samples:
        # Додати нові зразки в emails.csv
        with open(DATA_PATH, 'a', newline='', encoding='utf-8') as ef:
            writer = csv.DictWriter(ef, fieldnames=['text', 'label'])
            for row in new_samples:
                writer.writerow({'text': row['text'], 'label': row['label']})

        print(f"✅ Додано {len(new_samples)} нових прикладів до emails.csv")
        os.remove(new_data_file)

# --- Завантаження основних даних ---
df = pd.read_csv(DATA_PATH)
X = df['text'].astype(str)
y = df['label'].astype(int)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('clf', LogisticRegression(max_iter=1000))
])

model.fit(X_train, y_train)
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"✅ Модель навчено! Accuracy: {round(accuracy * 100, 2)}%")

joblib.dump(model, 'phishing_model.pkl')
print("✅ Збережено модель у phishing_model.pkl")
