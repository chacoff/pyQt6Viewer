import pandas as pd

# Load Csv1 and Csv2
csv1_path = 'ZH026_3260_34K_Datetime_clustered_data.csv'  # Replace with the actual path to Csv1
csv2_path = 'ZH026_3260_34K_excluded_Datetime.csv'  # Replace with the actual path to Csv2

csv1 = pd.read_csv(csv1_path)
csv2 = pd.read_csv(csv2_path)

result_df = csv2.merge(csv1[['File', 'Cluster']], on='File', how='left')

print(result_df['Cluster'].value_counts())

save: bool = False
if save:
    result_df.to_csv('ZH026_3260_34K_underbyBeam.csv', index=False)
