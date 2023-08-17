import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df: pd = pd.DataFrame()

csv1 = pd.read_csv('ZH026_3260_34K_Datetime_clustered_data.csv')
csv2 = pd.read_csv('ZH026_3260_34K_underbyBeam.csv')

csv1.drop(columns=['Modification Date', 'Timestamp'], inplace=True)
csv2.drop(columns=['Ground_truth', 'Predict'], inplace=True)

df['Total_Class'] = csv1['Cluster'].value_counts().sort_index()[0:100]
df['Wrong_Class'] = csv2['Cluster'].value_counts().sort_index()[0:100]

df = df.fillna(0)

total_mean = df['Total_Class'].mean()
print(f'average Total per image: {total_mean}')
wrong_mean = df['Wrong_Class'].mean()
print(f'average Wrong per image: {wrong_mean}')

# @çao said is not necessary
df = df.assign(Good_Class=df['Total_Class'] - df['Wrong_Class'])
df.drop(columns=['Total_Class'], inplace=True)

df.plot(kind='bar', stacked=True, color=['#828790', '#ff8b53'])
plt.xlabel('Beams')
plt.ylabel('Counts')
plt.xticks([])
plt.tight_layout()
plt.show()

