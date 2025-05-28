import google.generativeai as genai

genai.configure(api_key="встав_сюди_свій_API_ключ")

# Виводимо список доступних моделей
models = genai.list_models()

for model in models:
    print(f"🔹 {model.name}")
