import pandas as pd
# !!! ИЗМЕНЕНА БИБЛИОТЕКА !!!
import pymorphy3
from replacements.tech_replacements import TECH_REPLACEMENTS

# Теперь инициализация должна работать без ошибок
morph = pymorphy3.MorphAnalyzer()


def apply_normalization(text, replacement_dict):
    """Применяет словарь замен к одной строке текста (для Метод/Продукты)."""
    if not isinstance(text, str) or not text:
        return text.strip()

    text = text.lower().strip()

    # Замена синонимов
    for old, new in replacement_dict.items():
        text = text.replace(old, new)

    return text


def lemmatize_russian_text(text):
    """Приводит каждое слово в тексте к его нормальной форме (лемме) с помощью PyMorphy3."""
    if not isinstance(text, str) or not text:
        return ""

    # Очистка от знаков препинания и токенизация
    words = text.lower().replace('.', ' ').replace(',', ' ').split()
    lemmas = []

    for word in words:
        parsed = morph.parse(word)
        if parsed:
            # Используем новый morph
            lemmas.append(parsed[0].normal_form)

    return " ".join(lemmas)