import pandas as pd
import os
import numpy as np
from numpy import loadtxt
import keyboard
import cv2

source = 'ZH026_ALL_revision_2.0.csv'
name = source.split('.')[0]
root_dir = os.path.join(os.getcwd(), '00_JG-SB_Validation01_2022_02_11-28')
recheck = os.path.join(root_dir, 'zh026_recheck3.txt')
lines = loadtxt(recheck, comments="#", delimiter=",", unpack=False).astype(int)

df = pd.read_csv(source)
df.index += 2  # to fit the lines in the CSV
# print(df.head())

for item in lines:
    image_string = os.path.join(root_dir, df['Location'][item], df['ImageName'][item])
    print(f'before: {df.loc[[item]].to_string(header=False)}')
    img = cv2.imread(image_string)
    scale_percent = 30  # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    im = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

    cv2.imshow('', im)
    cv2.waitKey() & 0xFF

    if keyboard.read_key() == "s":

        df.loc[item, 'NewLabel'] = 'Seams'
        print(f'after: {df.loc[[item]].to_string(header=False)}\n')


df.to_csv(name+'_revision_3.0.csv', index=False)

