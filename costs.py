import matplotlib.pyplot as plt

methods = ['Ручной поиск', 'Классический поиск', 'WoodMind']
time = [960, 120, 2] # время в минутах

plt.figure(figsize=(8,5))
plt.barh(methods, time, color=['red', 'gray', 'green'])
plt.xlabel('Время анализа (мин)')
plt.title('Сравнение временных затрат на аналитическое исследование')
plt.savefig("fig_15.png", dpi=300)