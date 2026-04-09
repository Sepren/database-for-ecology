import matplotlib.pyplot as plt
import numpy as np

labels = ['Title-only', 'Abstract-only', 'Multi-source (WoodMind)']
pre = [0.62, 0.75, 0.88]
rec = [0.45, 0.68, 0.84]

x = np.arange(len(labels))
width = 0.35

fig, ax = plt.subplots()
ax.bar(x - width/2, pre, width, label='Precision', color='#2E86C1')
ax.bar(x + width/2, rec, width, label='Recall', color='#F39C12')

ax.set_ylabel('Значение')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()
plt.savefig("fig_12.png", dpi=300)