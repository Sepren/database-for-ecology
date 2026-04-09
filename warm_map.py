import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

data = [[15, 2, 5], [1, 10, 3], [4, 1, 12]]
df = pd.DataFrame(data, columns=['Биоэтанол', 'Наноцеллюлоза', 'Ксилит'],
                  index=['Гидролиз', 'Ферментация', 'Пиролиз'])

plt.figure(figsize=(8,6))
sns.heatmap(df, annot=True, cmap="YlGnBu")
plt.title("Матрица пересечения Методов и Продуктов")
plt.savefig("fig_13.png", dpi=300)