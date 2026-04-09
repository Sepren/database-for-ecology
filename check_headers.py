import pandas as pd

# Читаем только заголовки (0 строк)
try:
    df = pd.read_excel("data/merged_documents.xlsx", nrows=0, engine='openpyxl')
    print("\n--- 🔍 РЕАЛЬНЫЕ ЗАГОЛОВКИ В ТВОЕМ EXCEL ---")
    print(df.columns.tolist())
    print("-------------------------------------------\n")
except Exception as e:
    print(f"Ошибка чтения: {e}")