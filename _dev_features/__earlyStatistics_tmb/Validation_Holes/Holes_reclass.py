import pandas as pd
import os
import numpy as np
from numpy import loadtxt
import keyboard
import cv2

folder = 'Test_2022_08_30\\'
pattern = 'ZH026\\2341\\'
source = folder+'classified.txt'
cutoff = 1.0

data = pd.read_table(source, delimiter=' ', header=None)

data = data.iloc[:, 9:16]
data.drop(data.columns[[1, 2, 4, 5]], axis=1, inplace=True)

data.columns = ['ImageName', 'Defects', 'NoDefects']
data['Defects'] = data['Defects'].str.replace(r'%', '').str.replace(r',', '.').astype(float)
data['NoDefects'] = data['NoDefects'].str.replace(r'%', '').str.replace(r',', '.').astype(float)

total_images = data.shape[0]

data.drop(data.loc[data['NoDefects'] <= cutoff].index, inplace=True)

data_final = data.reset_index()
data_final = data_final.iloc[:, 1:]
print(data_final)
classified_images = data_final.shape[0]
classified_per = np.round_(100*(classified_images/total_images), 2)
print(f'Out of {total_images} images, with a threshold of {cutoff}%, '
      f'{classified_images} images were classified by the API, representing a {classified_per}%')

# root = 'T:\\Defects\\ZI550\\2350\\NoDefects'
for index, row in data_final.iterrows():
    namePNG = row['ImageName'].split('.')[0]+'.png'
    data_final.loc[index, 'ImageName'] = namePNG
    data_final.loc[index, 'Label'] = 'NoDefects'  # Prediction

    if row['NoDefects'] <= 95:
        data_final.loc[index, 'NewLabel'] = 'Defects'  # human clasified
    else:
        data_final.loc[index, 'NewLabel'] = 'NoDefects' # api clasified

    # data_final.loc[index, 'NewLabel'] = 'NoDefects'  # GroundTruth added later in the index_holes.py
    data_final.loc[index, 'Location'] = pattern+'NoDefects'
    # image_string = os.path.join(root, namePNG)
    # img = cv2.imread(image_string)

    # scale_percent = 75  # percent of original size
    # width = int(img.shape[1] * scale_percent / 100)
    # height = int(img.shape[0] * scale_percent / 100)
    # dim = (width, height)

    # im = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

    # cv2.imshow('', im)
    # cv2.waitKey() & 0xFF

    # if keyboard.read_key() == 'd':
    #    data_final.loc[index, 'GroundTruth'] = 'Defects'
    #    print(f'{data_final.loc[[index]].to_string(header=False)}')


data_final = data_final[['ImageName', 'Label', 'NewLabel', 'Location', 'Defects', 'NoDefects']]
csv_name = folder+'\\'+pattern.split('\\')[0]+'_'+pattern.split('\\')[1]+'_holes_checking_revisit_all_Images.csv'
data_final.to_csv(csv_name, index=False)
print(data_final)