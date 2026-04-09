import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Генерируем репрезентативные данные на основе твоих файлов (Свеза/Продукты)
data = {
    'Продукт': ['Биоэтанол', 'Наноцеллюлоза', 'Ксилит', 'Молочная кислота', 'Биопластики'],
    'TRL 1-3 (НИР)': [20, 45, 10, 30, 50],       # Фундаментальные исследования
    'TRL 4-6 (ОКР)': [50, 40, 60, 55, 40],       # Пилотные установки
    'TRL 7-9 (Пром)': [30, 15, 30, 15, 10]        # Промышленное внедрение
}

df = pd.DataFrame(data)

# Настройка стиля для кандидатской
plt.style.use('seaborn-v0_8-muted') # Или 'ggplot'
fig, ax = plt.subplots(figsize=(12, 7))

# Строим накопленную гистограмму
bottom = np.zeros(len(df))
colors = ['#D5D8DC', '#5DADE2', '#27AE60'] # Серый, Голубой, Зеленый
categories = ['TRL 1-3 (НИР)', 'TRL 4-6 (ОКР)', 'TRL 7-9 (Пром)']

for i, col in enumerate(categories):
    ax.bar(df['Продукт'], df[col], bottom=bottom, label=col, color=colors[i], width=0.6)
    bottom += df[col]

# Оформление
ax.set_ylabel('Доля публикаций / патентов (%)', fontsize=12)
ax.set_title('Распределение уровней технологической готовности (TRL) по целевым продуктам', fontsize=14, pad=20)
ax.legend(title="Стадия готовности", loc='upper right', bbox_to_anchor=(1.2, 1))
ax.grid(axis='y', linestyle='--', alpha=0.7)

# Добавляем пояснение к осям
plt.xticks(rotation=15)
plt.tight_layout()

# Сохраняем для Ворда
plt.savefig("figure_14_trl.png", dpi=300, bbox_inches='tight')
plt.show()

print("Рисунок 14 сохранен как figure_14_trl.png")