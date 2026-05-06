import streamlit as st
import pandas as pd
from core.orchestrator import Orchestrator
from ui.graph_visualizer import GraphVisualizer

# 1. Настройка страницы
st.set_page_config(page_title="WoodMind AI", layout="wide", page_icon="🌲")

# Лимит рёбер вокруг узла фокуса до нажатия «Показать все связи»
FOCUS_GRAPH_EDGE_PREVIEW = 150

# Первая порция строк на вкладке «База знаний» (ускоряет отрисовку)
KB_PREVIEW_ROWS = 200


def _method_product_tokens(val) -> list:
    if pd.isna(val) or not str(val).strip():
        return []
    return [
        x.strip()
        for x in str(val).split(",")
        if x.strip() and x.strip() != "Прочее"
    ]


def _incident_edges_in_row(row: pd.Series, focus: str) -> int:
    """Число рёбер method–product в строке, инцидентных узлу focus (как в PyVis)."""
    methods = _method_product_tokens(row["method_normalized"])
    products = _method_product_tokens(row["product_normalized"])
    if focus not in methods and focus not in products:
        return 0
    if not methods or not products:
        return 0
    return sum(1 for m in methods for p in products if m == focus or p == focus)


def count_incident_edges(df: pd.DataFrame, focus: str) -> int:
    if df is None or df.empty:
        return 0
    return int(sum(_incident_edges_in_row(row, focus) for _, row in df.iterrows()))


def _expand_ai_tags_for_stats(series: pd.Series) -> pd.Series:
    """Один тег — одно вхождение в статистике (как в графе), а не вся строка через запятую."""
    tags = []
    for val in series:
        if pd.isna(val):
            continue
        for part in str(val).split(","):
            t = part.strip()
            if t and t.lower() not in ("nan", "не определено", "none"):
                tags.append(t)
    return pd.Series(tags, dtype=str)


def subset_incident_edges_budget(df: pd.DataFrame, focus: str, max_edges: int) -> pd.DataFrame:
    """Первые строки датафрейма, пока суммарно не набрано >= max_edges инцидентных рёбер."""
    if df is None or df.empty or max_edges <= 0:
        return df if df is not None else pd.DataFrame()
    rows = []
    acc = 0
    for _, row in df.iterrows():
        e = _incident_edges_in_row(row, focus)
        if e == 0:
            continue
        rows.append(row)
        acc += e
        if acc >= max_edges:
            break
    if not rows:
        return df.head(150) if len(df) else df
    return pd.DataFrame(rows)


def main():
    st.title("🌲 WoodMind: Система анализа биорефайнинга")

    # 2. Загрузка данных
    @st.cache_data
    def load_data():
        orch = Orchestrator()
        df, _ = orch.run_pipeline()
        return df

    try:
        df = load_data()
    except Exception as e:
        st.error(f"Ошибка подключения к БД: {e}")
        return

    if df.empty:
        st.warning("База данных пуста! Запустите reset_db.py и ingest_data.py")
        return

    # --- SIDEBAR (ФИЛЬТРЫ) ---
    st.sidebar.header("🔍 Фильтры")

    # Поиск
    search_query = st.sidebar.text_input("Поиск (по всем полям)", "")

    # Фильтр по годам
    if 'publication_year' in df.columns and df['publication_year'].notna().any():
        min_year = int(df['publication_year'].min())
        max_year = int(df['publication_year'].max())
        if min_year < max_year:
            years = st.sidebar.slider("Год публикации", min_year, max_year, (min_year, max_year))
        else:
            years = (min_year, max_year)
    else:
        years = (1800, 2030)

    # Фильтр по TRL
    available_trls = []
    if 'trl_level' in df.columns:
        available_trls = sorted(df['trl_level'].dropna().unique())
    trl_filter = st.sidebar.multiselect("Уровень TRL", available_trls, default=available_trls)

    # По умолчанию — полная таблица; снимите галочку для компактного вида (5 столбцов)
    show_all_cols = st.sidebar.checkbox(
        "📂 Показать все столбцы датасета",
        value=True,
        help="Выключите, чтобы оставить только название, год, метод, продукт и ссылку.",
    )
    st.sidebar.markdown("---")

    # --- ЛОГИКА ФИЛЬТРАЦИИ (Создаем df_filtered) ---
    df_filtered = df.copy()

    # 1. Фильтр по годам
    if 'publication_year' in df_filtered.columns:
        df_filtered = df_filtered[
            (df_filtered['publication_year'] >= years[0]) &
            (df_filtered['publication_year'] <= years[1])
            ]

    # 2. Фильтр по TRL
    if 'trl_level' in df_filtered.columns and trl_filter:
        df_filtered = df_filtered[df_filtered['trl_level'].isin(trl_filter)]

    # 3. Поиск (ищет везде)
    if search_query:
        mask = df_filtered.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)
        df_filtered = df_filtered[mask]

    # Вывод количества найденного
    st.sidebar.markdown(f"**Найдено записей:** {len(df_filtered)}")
    # --- ЛОГИКА ВЫБОРА УЗЛА ДЛЯ ФОКУСА ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 Фокус для Графа")

    # Извлекаем уникальные значения, исключая None и пустые строки
    methods_list = [m for m in df['method_normalized'].unique() if m and pd.notna(m)]
    products_list = [p for p in df['product_normalized'].unique() if p and pd.notna(p)]

    # Объединяем, убираем дубликаты и сортируем только строковые значения
    all_options = sorted(list(set(methods_list + products_list)))

    focus_mode = st.sidebar.selectbox(
        "Выбрать центральный узел:",
        ["Все связи"] + all_options
    )

    def _cell_contains_token(series: pd.Series, token: str) -> pd.Series:
        """Совпадение с токеном в ячейках вида «A, B, C» (как в graph_visualizer)."""

        def _touches(val) -> bool:
            if pd.isna(val) or not str(val).strip():
                return False
            parts = {x.strip() for x in str(val).split(",") if x.strip()}
            return token in parts

        return series.apply(_touches)

    # Данные для графа: при фокусе — полная выборка по узлу (ограничение по рёбрам — на вкладке графа)
    if focus_mode != "Все связи":
        m_mask = _cell_contains_token(df_filtered["method_normalized"], focus_mode)
        p_mask = _cell_contains_token(df_filtered["product_normalized"], focus_mode)
        graph_df_focus_full = df_filtered[m_mask | p_mask]
    else:
        graph_df_focus_full = None

    if st.session_state.get("_graph_ui_focus") != focus_mode:
        st.session_state._graph_ui_focus = focus_mode
        st.session_state._graph_focus_show_all_links = False

    kb_filter_sig = (len(df_filtered), search_query, tuple(int(y) for y in years), tuple(trl_filter))
    if st.session_state.get("_kb_filter_sig") != kb_filter_sig:
        st.session_state._kb_filter_sig = kb_filter_sig
        st.session_state._kb_show_full_table = False

    # --- ОСНОВНЫЕ ВКЛАДКИ ---
    tabs = st.tabs(["📊 База Знаний", "🕸 Граф связей", "📈 Аналитика"])

    # Вкладка 1: ТАБЛИЦА
    with tabs[0]:
        st.subheader(f"Список публикаций ({len(df_filtered)})")

        n_kb = len(df_filtered)
        kb_show_all = st.session_state.get("_kb_show_full_table", False)
        if kb_show_all or n_kb <= KB_PREVIEW_ROWS:
            df_kb = df_filtered
        else:
            df_kb = df_filtered.head(KB_PREVIEW_ROWS)

        if n_kb > KB_PREVIEW_ROWS:
            if kb_show_all:
                st.caption(f"Показаны все {n_kb} записей (таблица может прогружаться дольше).")
                if st.button("Показать только первые 200 записей", key="kb_table_collapse"):
                    st.session_state._kb_show_full_table = False
                    st.rerun()
            else:
                st.caption(
                    f"Для быстрой загрузки показаны первые {KB_PREVIEW_ROWS} из {n_kb} записей "
                    f"(с учётом фильтров слева)."
                )
                if st.button(f"Показать все {n_kb} записей", key="kb_table_expand"):
                    st.session_state._kb_show_full_table = True
                    st.rerun()

        if show_all_cols:
            editor_kw = dict(
                use_container_width=True,
                hide_index=True,
                disabled=df_kb.columns,
            )
            if "url" in df_kb.columns:
                editor_kw["column_config"] = {
                    "url": st.column_config.LinkColumn(
                        "url",
                        help="Нажмите, чтобы открыть оригинал статьи",
                        validate=r"^http",
                        display_text="Открыть ссылку",
                    ),
                }
            st.data_editor(df_kb, **editor_kw)
        else:
            display_columns = {
                "title": "Название",
                "publication_year": "Год",
                "method_normalized": "Метод (AI)",
                "product_normalized": "Продукт (AI)",
                "url": "Ссылка на статью",
            }

            valid_cols = [c for c in display_columns.keys() if c in df_kb.columns]
            df_view = df_kb[valid_cols].rename(columns=display_columns)

            st.data_editor(
                df_view,
                column_config={
                    "Ссылка на статью": st.column_config.LinkColumn(
                        "Ссылка на статью",
                        help="Нажмите, чтобы открыть оригинал статьи",
                        validate=r"^http",
                        display_text="Открыть ссылку",
                    ),
                },
                use_container_width=True,
                hide_index=True,
                disabled=df_view.columns,
            )

    # Вкладка 2: ГРАФ
    with tabs[1]:
        st.subheader("Карта технологий")
        df_for_graph = None
        focus_node = None

        if focus_mode == "Все связи":
            df_for_graph = df_filtered.head(150)
            focus_node = None
            if len(df_filtered) > 150:
                st.info(
                    "💡 Режим «Все связи»: для скорости показаны только первые 150 записей выборки. "
                    "Выберите узел слева, чтобы увидеть его окружение."
                )
        elif graph_df_focus_full is None or graph_df_focus_full.empty:
            st.warning(f"Нет записей, где встречается узел «{focus_mode}» (с учётом фильтров слева).")
        else:
            focus_node = focus_mode
            total_edges = count_incident_edges(graph_df_focus_full, focus_mode)
            n_publ = len(graph_df_focus_full)
            show_all = st.session_state.get("_graph_focus_show_all_links", False)

            if total_edges <= FOCUS_GRAPH_EDGE_PREVIEW or show_all:
                df_for_graph = graph_df_focus_full
                edges_shown = total_edges
                st.caption(
                    f"Узел «{focus_mode}»: {n_publ} публикаций, {edges_shown} связей (рёбер method–product)."
                )
                if total_edges > FOCUS_GRAPH_EDGE_PREVIEW:
                    if st.button("Показать только первые 150 связей", key="graph_focus_collapse"):
                        st.session_state._graph_focus_show_all_links = False
                        st.rerun()
            else:
                df_for_graph = subset_incident_edges_budget(
                    graph_df_focus_full, focus_mode, FOCUS_GRAPH_EDGE_PREVIEW
                )
                edges_shown = count_incident_edges(df_for_graph, focus_mode)
                st.caption(
                    f"Узел «{focus_mode}»: показано {edges_shown} связей из {total_edges} "
                    f"({len(df_for_graph)} публикаций из {n_publ})."
                )
                if st.button(f"Показать все связи ({total_edges})", key="graph_focus_expand"):
                    st.session_state._graph_focus_show_all_links = True
                    st.rerun()

        try:
            if df_for_graph is not None and not df_for_graph.empty:
                viz = GraphVisualizer()
                path = viz.generate_html(df_for_graph, focus_node=focus_node)
                viz.display(path)
        except Exception as e:
            st.warning(f"Граф пока не готов (нет данных для связей): {e}")

    # Вкладка 3: СТАТИСТИКА (Исправленная)
    with tabs[2]:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Топ методов (AI)**")
            if "method_normalized" in df_filtered.columns:
                methods_expanded = _expand_ai_tags_for_stats(df_filtered["method_normalized"])
                counts = methods_expanded.value_counts().head(15)
                if counts.empty:
                    st.info("Нет данных")
                else:
                    st.bar_chart(counts)
            else:
                st.warning("Колонка 'method_normalized' отсутствует.")

        with col2:
            st.markdown("**Топ продуктов (AI)**")
            if "product_normalized" in df_filtered.columns:
                products_expanded = _expand_ai_tags_for_stats(df_filtered["product_normalized"])
                counts = products_expanded.value_counts().head(15)
                if counts.empty:
                    st.info("Нет данных")
                else:
                    st.bar_chart(counts)
            else:
                st.warning("Колонка 'product_normalized' отсутствует.")

        st.markdown("---")
        st.markdown("**Статистика по годам для продуктовых исследований**")
        if "product_normalized" in df_filtered.columns and "publication_year" in df_filtered.columns:
            valid_products_mask = (
                df_filtered["product_normalized"]
                .fillna("")
                .astype(str)
                .str.strip()
                .ne("")
            )
            yearly_product_counts = (
                df_filtered.loc[valid_products_mask, "publication_year"]
                .dropna()
                .astype(int)
                .value_counts()
                .sort_index()
            )

            if yearly_product_counts.empty:
                st.info("Нет данных по годам для продуктовых исследований.")
            else:
                st.line_chart(yearly_product_counts)
                st.dataframe(
                    yearly_product_counts.rename("Количество исследований").to_frame(),
                    use_container_width=True,
                )
        else:
            st.warning("Нужны колонки 'product_normalized' и 'publication_year'.")


if __name__ == "__main__":
    main()