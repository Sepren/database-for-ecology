import pymorphy3
import re
import pandas as pd

morph = pymorphy3.MorphAnalyzer()

def lemmatize_text(text):
    """Приводит текст к нормальной форме (например: 'методами' -> 'метод')"""
    if not isinstance(text, str) or not text:
        return ""
    # Оставляем только буквы и пробелы
    text = re.sub(r'[^\w\s-]', ' ', text.lower())
    words = text.split()
    return " ".join([morph.parse(word)[0].normal_form for word in words])

def clean_trl(val):
    """Вытаскивает цифру из TRL (например 'TRL 6 (tested)' -> 6)"""
    if pd.isna(val):
        return 0
    match = re.search(r'\d+', str(val))
    return int(match.group()) if match else 0