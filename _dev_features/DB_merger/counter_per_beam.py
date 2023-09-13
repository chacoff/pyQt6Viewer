import pandas as pd
import numpy as np
import re

df = pd.read_csv('ZH024-026-028-030/ZH024_filtered.csv', header=None, names=['FileName', 'Ground_truth', 'Predict'])

# Extract the third number from the filename using regex
df['Pattern'] = df['FileName'].str.extract(r'_(\d+)_WEB\d+\.bmp')

value_counts: pd = df['Pattern'].value_counts()
filtered_value_counts: pd = value_counts[value_counts >= 10]
average_count: float = filtered_value_counts.mean()
print(f'average images per beam: {round(average_count, 1)}')

count_dict_over: dict = {}
count_dict_under: dict = {}

for _, row in df.iterrows():
    beam_number = row['Pattern']

    if beam_number not in count_dict_over and beam_number not in count_dict_under:
        count_dict_over[beam_number] = 0
        count_dict_under[beam_number] = 0

    over_detection = row['Ground_truth'] == 'NoSeams' and row['Predict'] == 'Seams'
    under_detection = row['Ground_truth'] == 'Seams' and row['Predict'] == 'NoSeams'

    if over_detection:
        count_dict_over[beam_number] += 1

    if under_detection:
        count_dict_under[beam_number] += 1

# for beam_number, count in count_dict.items():
#     print(f"Beam Number: {beam_number}, Occurrences: {count}")

grouped_dict: list = [('over detection', count_dict_over), ('under detection', count_dict_under)]

for dictio_name, dictio in grouped_dict:
    total_count: int = sum(dictio.values())
    num_unique_beam: int = len(dictio)
    average: float = round(total_count / num_unique_beam if num_unique_beam > 0 else 0, 2)
    print(f'average {dictio_name}: {average} ({round(average*100/average_count, 2)}%)')
