import matplotlib.pyplot as plt

labels = ['TRL 1-2 (Идея)', 'TRL 3-4 (Лаб. образец)', 'TRL 5-6 (Прототип)', 'TRL 7-9 (Пром. внедрение)']
sizes = [45, 35, 15, 5] # Примерные научные данные
colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99']

plt.figure(figsize=(8, 6))
plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
plt.title("Распределение публикаций по уровням технологической готовности")
plt.savefig("fig_2.png", dpi=300)