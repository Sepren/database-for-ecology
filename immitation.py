# visual_generator.py

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import networkx as nx
from pyvis.network import Network
import re

# --- Импортируем наши модули ---
from main_data_loader import load_clean_data_from_db
from data_processor import apply_normalization
from replacements.tech_replacements import TECH_REPLACEMENTS
from replacements.method_taxonomy import METHOD_TAXONOMY

print("Все библиотеки и модули успешно импортированы.")

# --- ШАГ 0: ЗАГРУЗКА И ПОДГОТОВКА ДАННЫХ ---
try:
    df = load_clean_data_from_db()
    if df.empty:
        raise ValueError("Данные не загружены.")
    df.columns = [x.lower() for x in df.columns]
    print(f"Данные успешно загружены ({len(df)} строк). Имена столбцов нормализованы.")
except Exception as e:
    print(f"КРИТИЧЕСКАЯ ОШИБКА на этапе загрузки данных: {e}")
    exit()
# --- ШАГ 1: УЛУЧШЕННАЯ ВИЗУАЛИЗАЦИЯ TRL ---
try:
    print("\n[Шаг 1/3] Начинаю улучшенную визуализацию TRL...")
    if 'trl' not in df.columns:
        raise KeyError("Столбец 'trl' не найден в данных!")

    trl_data = df['trl'].copy()
    trl_numeric = pd.to_numeric(trl_data, errors='coerce')
    trl_categorized = trl_numeric.fillna('Не определено').astype(str)

    # Убираем ".0" из числовых значений для красоты
    trl_categorized = trl_categorized.str.replace('.0', '', regex=False)

    order = [str(i) for i in range(1, 10)] + ['Не определено']

    plt.figure(figsize=(12, 8))
    sns.set_theme(style="whitegrid")
    ax = sns.countplot(x=trl_categorized, order=order, palette="viridis")

    ax.set_title('Распределение публикаций по Уровню Технологической Готовности (TRL)', fontsize=16, pad=20)
    ax.set_xlabel('Уровень TRL', fontsize=12)
    ax.set_ylabel('Количество публикаций', fontsize=12)

    for p in ax.patches:
        ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', xytext=(0, 9), textcoords='offset points', fontsize=10)

    plt.tight_layout()
    plt.savefig('trl_distribution_improved.png', dpi=300)
    print("-> Успешно! График 'trl_distribution_improved.png' сохранен.")

except KeyError as e:
    print(f"-> Ошибка при обработке TRL: {e}")

# --- ШАГ 2: КЛАССИФИКАЦИЯ МЕТОДОВ И ВИЗУАЛИЗАЦИЯ ---
try:
    print("\n[Шаг 2/3] Начинаю классификацию методов...")
    if 'метод' not in df.columns:
        raise KeyError("Столбец 'метод' не найден в данных!")

    method_to_category = {method.lower(): category for category, methods in METHOD_TAXONOMY.items() for method in
                          methods}


    def classify_method(text):
        if not isinstance(text, str):
            return "Не определено"
        # Сначала нормализуем текст (приводим синонимы к базе)
        normalized_text = apply_normalization(text.lower(), TECH_REPLACEMENTS)
        # Затем ищем вхождения ключевых слов из таксономии
        for method_keyword, category in method_to_category.items():
            if method_keyword in normalized_text:
                return category
        return "Прочие"


    df['метод_категория'] = df['метод'].apply(classify_method)

    plt.figure(figsize=(14, 8))
    ax2 = sns.countplot(y='метод_категория', data=df, order=df['метод_категория'].value_counts().index,
                        palette="plasma")
    ax2.set_title('Распределение исследований по категориям методов', fontsize=16, pad=20)
    ax2.set_xlabel('Количество публикаций', fontsize=12)
    ax2.set_ylabel('Категория метода', fontsize=12)
    plt.tight_layout()
    plt.savefig('method_categories.png', dpi=300)
    print("-> Успешно! График 'method_categories.png' сохранен.")

except KeyError as e:
    print(f"-> Ошибка при классификации методов: {e}")

# --- НОВЫЙ ШАГ: ИЗВЛЕЧЕНИЕ ЧИСТЫХ МЕТОДОВ ДЛЯ АНАЛИЗА ---
print("\n[Новый шаг] Извлекаю чистые методы из текста аннотаций...")

# Создаем один большой список всех возможных ключевых слов методов
all_method_keywords = [method for methods in METHOD_TAXONOMY.values() for method in methods]


def extract_clean_methods_from_text(text):
    """Ищет ключевые слова методов из таксономии в тексте."""
    if not isinstance(text, str):
        return ""

    found_methods = set()  # Используем set для автоматической уникальности
    text_lower = text.lower()

    for keyword in all_method_keywords:
        # Ищем точное слово, чтобы 'синтез' не находил 'биосинтез' в общем поиске
        if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
            # Применяем нормализацию, чтобы "ферментативный гидролиз" стал "ферментация"
            normalized_method = apply_normalization(keyword, TECH_REPLACEMENTS)
            found_methods.add(normalized_method)

    return ", ".join(sorted(list(found_methods)))


# Применяем функцию к столбцу 'аннотация' (или 'содержание', если он лучше)
# Убедимся, что столбец 'аннотация' существует
if 'аннотация' in df.columns:
    df['метод_clean'] = df['аннотация'].apply(extract_clean_methods_from_text)
    print("-> Успешно! Создан столбец 'метод_clean' на основе аннотаций.")
else:
    print("-> Ошибка: столбец 'аннотация' не найден! Граф не может быть построен.")
    exit()

# --- ШАГ 3: ПОСТРОЕНИЕ ГРАФА ЗНАНИЙ (на чистых данных) ---
try:
    print("\n[Шаг 3/5] Начинаю построение графа знаний на ЧИСТЫХ данных...")
    # ИСПОЛЬЗУЕМ 'метод_clean' ВМЕСТО 'метод'
    df_graph = df.copy()
    df_graph.dropna(subset=['метод_clean', 'продукты_ml'], inplace=True)
    df_graph = df_graph[(df_graph['продукты_ml'] != 'не найдено') & (df_graph['продукты_ml'].str.len() > 0) & (
                df_graph['метод_clean'].str.len() > 0)]

    sample_size = min(500, len(df_graph))  # Увеличим сэмпл для более репрезентативного графа
    if sample_size == 0:
        raise ValueError("Нет данных для построения графа после фильтрации.")

    df_sample = df_graph.sample(n=sample_size, random_state=42)
    print(f"Для графа будет использовано {sample_size} записей.")

    G = nx.Graph()

    method_to_category = {method.lower(): category for category, methods in METHOD_TAXONOMY.items() for method in
                          methods}


    def classify_method(text):
        if not isinstance(text, str): return "Не определено"
        normalized_text = apply_normalization(text.lower(), TECH_REPLACEMENTS)
        for method_keyword, category in method_to_category.items():
            if method_keyword in normalized_text: return category
        return "Прочие"


    df_sample['метод_категория'] = df_sample['метод_clean'].apply(classify_method)

    category_colors = {
        "Химические методы": "#FF5733", "Ферментативные методы": "#33FF57", "Термические методы": "#FF33A1",
        "Методы предобработки": "#33A1FF", "Биологические методы": "#A1FF33", "Физические методы": "#F3FF33",
        "Комбинированные методы": "#8D33FF", "Механические методы": "#FF8D33", "Методы экстракции": "#33FFF3",
        "Прочие": "#AAAAAA", "Не определено": "#555555"
    }

    for _, row in df_sample.iterrows():
        methods_raw = str(row['метод_clean']).split(',')  # ИСПОЛЬЗУЕМ 'метод_clean'
        products_raw = str(row['продукты_ml']).split(',')
        category = row.get('метод_категория', 'Прочие')

        clean_methods = [m.strip() for m in methods_raw if m.strip()]
        clean_products = [p.strip().lower() for p in products_raw if p.strip()]

        for method in set(clean_methods):
            G.add_node(method, type='method', color=category_colors.get(category, '#AAAAAA'), size=15)
            for product in set(clean_products):
                G.add_node(product, type='product', color='#8A2BE2', size=10)
                if G.has_edge(method, product):
                    G[method][product]['weight'] += 1
                else:
                    G.add_edge(method, product, weight=1)

    G.remove_nodes_from(list(nx.isolates(G)))
    nt = Network(notebook=False, height="800px", width="100%", bgcolor="#222222", font_color="white",
                 cdn_resources='in_line')
    nt.from_nx(G)
    with open("knowledge_graph_clean.html", "w", encoding="utf-8") as file:
        file.write(nt.generate_html())
    print("-> Успешно! Чистый граф 'knowledge_graph_clean.html' сохранен.")
except (KeyError, ValueError) as e:
    print(f"-> Ошибка при построении графа: {e}")

try:
    print("\n[Шаг 4/5] Начинаю количественный анализ ЧИСТОГО графа...")
    if 'G' not in locals() or G.number_of_nodes() == 0:
        raise ValueError("Граф 'G' не был создан или пуст.")

    method_nodes = [n for n, d in G.nodes(data=True) if d['type'] == 'method']
    degrees = {node: G.degree(node) for node in method_nodes}
    top_10_methods = sorted(degrees.items(), key=lambda item: item[1], reverse=True)[:10]

    product_nodes = [n for n, d in G.nodes(data=True) if d['type'] == 'product']
    product_degrees = {node: G.degree(node) for node in product_nodes}
    top_10_products = sorted(product_degrees.items(), key=lambda item: item[1], reverse=True)[:10]

    print("\n--- [РЕЗУЛЬТАТ] ТОП-10 ЧИСТЫХ МЕТОДОВ ---")
    print(pd.DataFrame(top_10_methods, columns=['Метод', 'Количество связей']))
    print("\n--- [РЕЗУЛЬТАТ] ТОП-10 ЧИСТЫХ ПРОДУКТОВ ---")
    print(pd.DataFrame(top_10_products, columns=['Продукт', 'Количество связей']))

    print("\n[Шаг 5/5] Создаю визуализации для ЧИСТЫХ ТОП-10...")

    top_methods_df = pd.DataFrame(top_10_methods, columns=['Метод', 'Количество связей'])
    plt.figure(figsize=(12, 8))
    ax_m = sns.barplot(x='Количество связей', y='Метод', data=top_methods_df, palette='viridis')
    ax_m.set_title('ТОП-10 методов по количеству связей с продуктами', fontsize=16, pad=20)
    plt.tight_layout()
    plt.savefig('top_10_methods_clean.png', dpi=300)
    print("-> Успешно! График 'top_10_methods_clean.png' сохранен.")

    top_products_df = pd.DataFrame(top_10_products, columns=['Продукт', 'Количество связей'])
    plt.figure(figsize=(12, 8))
    ax_p = sns.barplot(x='Количество связей', y='Продукт', data=top_products_df, palette='plasma')
    ax_p.set_title('ТОП-10 продуктов по количеству связей с методами', fontsize=16, pad=20)
    plt.tight_layout()
    plt.savefig('top_10_products_clean.png', dpi=300)
    print("-> Успешно! График 'top_10_products_clean.png' сохранен.")

except ValueError as e:
    print(f"-> Ошибка при анализе графа: {e}")

print("\nВсе задачи выполнены.")

