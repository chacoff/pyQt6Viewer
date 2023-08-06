import pandas as pd

pd_random = pd.read_csv('sample_list_1094_total66168.csv', usecols=['Location'])

name_list = []
for index, row in pd_random.iterrows():
    name = row['Location'].split('\\')[-1]
    pd_random.loc[index, 'Label'] = 'No Seams'
    pd_random.loc[index, 'NewLabel'] = 'No Seams'
    name_list.append(name)

pd_random['ImageName'] = pd.Series(name_list)
pd_random = pd_random[['ImageName', 'Label', 'NewLabel', 'Location']]
pd_random.to_csv(f'sample_list_Val3.csv', index=False)