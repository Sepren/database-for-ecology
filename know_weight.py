import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()
G.add_edge("Метод A", "Продукт 1", weight=10)
G.add_edge("Метод A", "Продукт 2", weight=2)
G.add_edge("Метод B", "Продукт 1", weight=5)

pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=3000, font_size=10)
labels = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
plt.savefig("fig_8.png", dpi=300)