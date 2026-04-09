import networkx as nx
from pyvis.network import Network
import pandas as pd
import os


class GraphVisualizer:
    """
    Класс для построения интерактивных графов связей (Метод -> Продукт).
    """

    def __init__(self):
        self.net = None

    def generate_graph(self, df: pd.DataFrame, source_col='Method', target_col='Product', filename='graph.html'):
        """
        Генерирует HTML-файл с графом.
        :param df: DataFrame с данными
        :param source_col: Колонка-источник (откуда стрелка)
        :param target_col: Колонка-цель (куда стрелка)
        :param filename: Имя файла для сохранения
        :return: Путь к сохраненному файлу
        """
        # Проверка наличия колонок
        if source_col not in df.columns or target_col not in df.columns:
            print(f"[GraphVisualizer] Ошибка: Колонки {source_col} или {target_col} не найдены.")
            return None

        # Создаем граф NetworkX из DataFrame
        # Берем первые 100 связей, чтобы не перегружать браузер при тесте
        df_limit = df.head(100)
        G = nx.from_pandas_edgelist(df_limit, source=source_col, target=target_col)

        # Инициализируем PyVis
        self.net = Network(height='600px', width='100%', bgcolor='#222222', font_color='white')

        # Переносим данные из NetworkX в PyVis
        self.net.from_nx(G)

        # Настройки физики (чтобы узлы красиво разлетались)
        self.net.set_options("""
        var options = {
          "physics": {
            "barnesHut": {
              "gravitationalConstant": -8000,
              "springLength": 250,
              "springConstant": 0.001
            },
            "minVelocity": 0.75
          }
        }
        """)

        # Сохранение
        try:
            self.net.save_graph(filename)
            return filename
        except Exception as e:
            print(f"[GraphVisualizer] Ошибка при сохранении графа: {e}")
            return None