import streamlit as st
import pandas as pd
import plotly.express as px
# Импортируем классы (убедитесь, что папки помечены как Sources Root)
from core.orchestrator import Orchestrator
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

# Настройка страницы (должна быть самой первой командой Streamlit)
st.set_page_config(page_title="WoodMind AI System", layout="wide")


def main():
    st.title("🌲 WoodMind: Мультиагентная система")
    st.markdown("**Заказчик:** НАО «СВЕЗА» | **Исполнитель:** Ун-т ИТМО")

    # 1. Инициализация Оркестратора
    try:
        orchestrator = Orchestrator()
    except Exception as e:
        st.error(f"Ошибка инициализации системы: {e}")
        return

    # 2. Боковая панель
    st.sidebar.header("Панель управления")
    action = st.sidebar.radio("Выберите модуль:",
                              ["База знаний (Data)", "AI Аналитика (Agents)", "Граф связей (Knowledge Graph)"])

    # 3. Загрузка данных (с кэшированием в сессии)
    if 'data' not in st.session_state:
        with st.spinner('Агенты опрашивают базу данных...'):
            try:
                # Запускаем пайплайн
                df, stats = orchestrator.run_analysis_pipeline()

                # Проверка: вернулись ли данные?
                if df is None or df.empty:
                    st.error("⚠️ Данные не найдены! Проверьте:")
                    st.markdown("1. Подключена ли база данных в `config.py`?")
                    st.markdown("2. Лежит ли файл Excel в папке `data/`?")
                    # Создаем пустой DF, чтобы интерфейс не падал
                    st.session_state['data'] = pd.DataFrame()
                    st.session_state['stats'] = pd.DataFrame()
                else:
                    st.success(f"Загружено {len(df)} записей.")
                    st.session_state['data'] = df
                    st.session_state['stats'] = stats
            except Exception as e:
                st.error(f"Критическая ошибка при загрузке: {e}")
                st.session_state['data'] = pd.DataFrame()

    # Получаем данные из сессии
    df = st.session_state.get('data')

    # Если данных нет — останавливаем выполнение, чтобы не было ошибок дальше
    if df is None or df.empty:
        st.warning("Режим ожидания данных...")
        return

    # --- ВКЛАДКА 1: ДАННЫЕ ---
    if action == "База знаний (Data)":
        st.subheader("Реестр научных источников")
        st.dataframe(df.head(50))

    # --- ВКЛАДКА 2: АНАЛИТИКА ---
    elif action == "AI Аналитика (Agents)":
        st.subheader("Статистический анализ")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Распределение по TRL")
            if 'trl' in df.columns:
                try:
                    fig = px.bar(df['trl'].value_counts(), title="Уровень тех. готовности")
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as ex:
                    st.error(f"Ошибка графика TRL: {ex}")
            else:
                st.warning("Нет колонки 'trl'")

        with col2:
            st.markdown("### Топ Методов")
            if 'method' in df.columns:
                try:
                    top_methods = df['method'].value_counts().head(10)
                    fig2 = px.pie(values=top_methods.values, names=top_methods.index, title="Популярные технологии")
                    st.plotly_chart(fig2, use_container_width=True)
                except Exception as ex:
                    st.error(f"Ошибка графика методов: {ex}")

    # --- ВКЛАДКА 3: ГРАФ ---
    elif action == "Граф связей (Knowledge Graph)":
        st.subheader("Семантический граф")
        if 'method' in df.columns and 'product' in df.columns:
            try:
                from utils.visualization import GraphVisualizer
                viz = GraphVisualizer()
                path = viz.generate_graph(df, source_col='method', target_col='product')
                if path:
                    with open(path, 'r', encoding='utf-8') as f:
                        source_code = f.read()
                    components.html(source_code, height=600)
            except Exception as e:
                st.error(f"Ошибка построения графа: {e}")
        else:
            st.warning("Недостаточно данных для графа.")


if __name__ == "__main__":
    main()