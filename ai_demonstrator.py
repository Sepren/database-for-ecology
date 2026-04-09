import pandas as pd
import networkx as nx
from main_data_loader import load_clean_data_from_db
from data_processor import apply_normalization, lemmatize_russian_text
from replacements.tech_replacements import TECH_REPLACEMENTS
from transformers import pipeline  # Для имитации NER


# --- 1. Имитация NER (Центральный пункт доклада) ---

def ner_inference_placeholder(text):
    """
    Имитация инференса тонко настроенной LLM для извлечения сущностей.
    В докладе вы говорите о few-shot LLaMA 7B.
    Здесь используем упрощенный подход для демонстрации принципа.
    """
    example_methods = []
    example_products = []

    # Имитация извлечения на основе ключевых слов в тексте (Аннотация/Содержание)
    if "пиролиз" in text.lower() or "термо" in text.lower():
        example_methods.append("пиролиз")
    if "гидролиз" in text.lower() or "фермента" in text.lower():
        example_methods.append("гидролиз")

    if "целлюлоза" in text.lower() or "биоэтанол" in text.lower():
        example_products.append("целлюлоза")
    if "лигнин" in text.lower() and "биомасса" in text.lower():
        example_products.append("лигнин")

    # Добавьте реальную логику из вашей LLM-модели

    return {
        'Методы_NER': ", ".join(set(example_methods)),
        'Продукты_NER': ", ".join(set(example_products))
    }


# --- 2. Визуализация Связей (Визуальный элемент доклада) ---

def build_and_analyze_graph(df, method_col='Метод', product_col='Продукты_ml'):
    # ИСПРАВЛЕНИЕ: Используем переданные аргументы (method_col, product_col)
    # вместо жестко заданных имен ('Методы_NER', 'Продукты_NER')

    # 1. Фильтрация. Использование имен столбцов, переданных в функцию
    df_relations = df[[method_col, product_col]].dropna()

    G = nx.Graph()

    for index, row in df_relations.iterrows():
        # 2. Получение данных. Использование имен столбцов, переданных в функцию
        methods_str = str(row[method_col])
        products_str = str(row[product_col])

        methods = methods_str.split(', ')
        products = products_str.split(', ')

        for method in methods:
            m = method.strip()
            if not m: continue

            # Добавление узла метода с атрибутом type='method'
            G.add_node(m, type='method')

            for product in products:
                p = product.strip()
                if not p: continue

                # Добавление узла продукта с атрибутом type='product'
                G.add_node(p, type='product')

                # Добавление ребра (связи)
                # Увеличение веса, если ребро уже существует
                if G.has_edge(m, p):
                    G[m][p]['weight'] += 1
                else:
                    G.add_edge(m, p, weight=1)

    return G

# --- 3. Основная Логика (Запуск Демонстрации) ---

if __name__ == '__main__':
    # 1. Загрузка очищенных данных
    df_clean = load_clean_data_from_db()

    if df_clean.empty:
        print("Ошибка: Данные не загружены. Проверьте параметры подключения в main_data_loader.py")
        exit()

    print(f"Загружено {len(df_clean)} строк.")

    # 2. Демонстрация: PyMorphy3 (Слайд 5)
    print("\n--- Демонстрация PyMorphy3 (Улучшенный Поиск) ---")

    # Используем русский текст, чтобы продемонстрировать лемматизацию
    sample_text = "Технологии биоконверсии древесных отходов являются самыми перспективными для экологии."
    lemmatized_text = lemmatize_russian_text(sample_text)

    print(f"Исходный текст: {sample_text}")
    print(f"Лемматизация:  {lemmatized_text}")
    # Вывод должен быть: технология биоконверсия древесный отход являться самый перспективный для экология

    # 3. Демонстрация: Ручная Нормализация (Справочники) (Слайд 6)
    print("\n--- Демонстрация Ручной Нормализации (Справочники) ---")

    # Используем четкий пример, который должен быть в словаре замен
    # Предполагаем, что "ферментативный гидролиз" должен стать "ферментация"
    sample_method = "ферментативный гидролиз"

    # Вызываем функцию нормализации
    normalized_method = apply_normalization(sample_method, TECH_REPLACEMENTS)

    print(f"Исходный метод: {sample_method}")
    print(f"Нормализованный: {normalized_method}")

    # 4. Демонстрация: NER/LLM и Построение Графа (Слайды 8-11)

    # 1. Фильтрация данных: Оставляем только те строки, где NER извлек хотя бы один метод/продукт.
    # Используем ПРАВИЛЬНЫЕ имена столбцов из вашей БД: 'Метод' и 'Продукты_ml'
    df_sample = df_clean.dropna(subset=['Метод', 'Продукты_ml'], how='any').head(100)  # Берем до 100 строк

    if df_sample.empty:
        print(
            "\n!!! КРИТИЧЕСКАЯ ОШИБКА: Колонки 'Методы_NER' или 'Продукты_NER' пусты во всей БД. NER-обработка не сработала.")
        print("Проверьте код заполнения этих колонок (например, LLM-вызовы).")
        exit()

    print("\n--- Демонстрация NER/LLM (Извлечение Сущностей) ---")

    # !!! ОБНОВИТЕ ЭТУ СТРОКУ для вывода ПРАВИЛЬНЫХ столбцов !!!
    print(df_sample[['Аннотация', 'Метод', 'Продукты_ml']].head().to_string())

    # 2. Построение Графа
    print("\n--- Построение графа связей Методы <-> Продукты ---")

    # !!! ОБНОВИТЕ ЭТУ СТРОКУ, чтобы передать в функцию build_and_analyze_graph ПРАВИЛЬНЫЕ имена колонок!!!
    G = build_and_analyze_graph(df_sample, method_col='Метод', product_col='Продукты_ml')

    if G.number_of_nodes() == 0:
        print("!!! КРИТИЧЕСКАЯ ОШИБКА: Граф все равно пуст. Проверьте функцию build_and_analyze_graph.")
        exit()

    print(f"Граф построен: {G.number_of_nodes()} узлов, {G.number_of_edges()} связей.")

    # 5. Демонстрация: Визуализация (Финальный Слайд)
    G = build_and_analyze_graph(df_sample)
    # Для визуализации можно использовать NetworkX (напечатать узлы) или экспортировать в Gephi/PyVis.
    print(f"\nНаиболее частые методы в сэмпле: {G.degree()}")