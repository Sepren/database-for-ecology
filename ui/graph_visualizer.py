from pyvis.network import Network
import streamlit.components.v1 as components
import os


class GraphVisualizer:
    def generate_html(self, df, focus_node=None):
        from pyvis.network import Network
        net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")

        # Настройка физики для "научного" вида
        net.barnes_hut(gravity=-2000, central_gravity=0.3, spring_length=150)

        def add_method_node(m: str) -> None:
            if m == "Прочее":
                return
            if focus_node is not None and m == focus_node:
                net.add_node(
                    m,
                    label=m,
                    color={
                        "background": "#E67E22",
                        "border": "#C0392B",
                        "highlight": {"background": "#EB984E", "border": "#922B21"},
                    },
                    borderWidth=4,
                    size=42,
                    font={"size": 16, "face": "arial", "color": "#1a1a1a"},
                    title="Технология (узел фокуса)",
                )
            else:
                net.add_node(m, label=m, color="#E67E22", size=25, title="Технология")

        def add_product_node(p: str) -> None:
            if p == "Прочее":
                return
            if focus_node is not None and p == focus_node:
                net.add_node(
                    p,
                    label=p,
                    color={
                        "background": "#27AE60",
                        "border": "#C0392B",
                        "highlight": {"background": "#2ECC71", "border": "#922B21"},
                    },
                    borderWidth=4,
                    size=38,
                    font={"size": 15, "face": "arial", "color": "#1a1a1a"},
                    title="Продукт (узел фокуса)",
                )
            else:
                net.add_node(p, label=p, color="#27AE60", size=20, title="Целевой продукт")

        for _, row in df.iterrows():
            # Разделяем записи типа "Метод1, Метод2"
            methods = [m.strip() for m in str(row["method_normalized"]).split(",") if m.strip()]
            products = [p.strip() for p in str(row["product_normalized"]).split(",") if p.strip()]

            for m in methods:
                if m == "Прочее":
                    continue
                add_method_node(m)
                for p in products:
                    if p == "Прочее":
                        continue
                    add_product_node(p)
                    w = 3 if focus_node and (m == focus_node or p == focus_node) else 1
                    net.add_edge(m, p, color="#BDC3C7", width=w)

        path = "graph.html"
        net.save_graph(path)
        return path

    def display(self, html_path):
        """Отображает HTML внутри Streamlit"""
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            components.html(source_code, height=620)
        except FileNotFoundError:
            components.html("<h3>Граф еще не построен</h3>")