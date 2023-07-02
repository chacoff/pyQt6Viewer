'''''''''
JG January 29, 2023
from the VoTT CSV to generate the darknet annotations, manifest, split and yaml
'''''''''

import os
import pandas as pd
import cv2
from tqdm import tqdm
import numpy as np
from numpy.random import seed
from numpy.random import randint
import yaml
pd.options.mode.chained_assignment = None  # default='warn'


def manifest_generator(vott_df, manifest_target, path):
    images_name = vott_df['image'].unique()
    for i in range(len(images_name)):
        file = open(manifest_target, "a")
        file.write(os.path.join(path, images_name[i])+'\n')
        file.close()
    print('INFO: Total number of images: %s' % len(images_name))


def csv2darknet(vott_df, labeldict, path):
    # Encode labels according to labeldict if code's don't exist
    if not "code" in vott_df.columns:
        vott_df['code'] = vott_df["label"].apply(lambda x: labeldict[x])
    # Round float to ints
    for col in vott_df[["xmin", "ymin", "xmax", "ymax"]]:
        vott_df[col] = (vott_df[col]).apply(lambda x: round(x))

    txt_file = ''
    last = ''
    print('INFO: number of annotations: %s' % len(vott_df))
    print('INFO: wait while converting to darknet ...')
    pbar = tqdm(total=len(vott_df))
    for index, row in vott_df.iterrows():
        img = cv2.imread(os.path.join(path, row["image"]), 0).shape
        # print(img[1], img[0])  # width and height
        xcen = float((row['xmin'] + row['xmax'])) / 2 / img[1]
        ycen = float((row['ymin'] + row['ymax'])) / 2 / img[0]
        w = float((row['xmax'] - row['xmin'])) / img[1]
        h = float((row['ymax'] - row['ymin'])) / img[0]
        xcen = round(xcen, 3)
        ycen = round(ycen, 3)
        w = round(w, 3)
        h = round(h, 3)
        target_name = row['image'].split('.')
        target = os.path.join(path, target_name[0] + '.txt')
        if not last == row['image']:
            txt_file = ''
            txt_file += "\n"
            txt_file += " ".join([str(x) for x in (row["code"], xcen, ycen, w, h)])
        else:
            txt_file += "\n"
            txt_file += " ".join([str(x) for x in (row["code"], xcen, ycen, w, h)])
            # txt_file += "\n"
        last = row['image']
        file = open(target, "w")
        file.write(txt_file[1:])  # the line with the calculation per annotation
        file.close()
        pbar.update(1)
    pbar.close()
    print('INFO: READY! VoTT CSV has been converted to Darknet Format')
    return True


def split_manifest(split=0.1, manifest_target='', val='', train=''):
    other_percentage = 1 - split
    f = open(manifest_target, "r")  # manifest.txt, a list with all the images
    lines = f.readlines()
    f.close()

    np.random.shuffle(lines)

    total_lines = len(lines)
    num_val = int(split * total_lines)
    num_train = int(total_lines - num_val)

    seed(5)
    lines_out = []  # list with the lines that will be removed later
    random_line = randint(0, total_lines, num_val)  # Vector with all the images (lines) we will use for validation
    #  print(random_line)
    f2 = open(val, 'w')
    for i in range(num_val):
        f2.writelines(lines[random_line[i]])
        lines_out.append(lines[random_line[i]])
    f2.close()

    training_lines = [x for x in lines if x not in lines_out]  # removed the lines_out from lines = full manifest here
    f3 = open(train, 'w')
    for j in range(num_train):
        f3.writelines(training_lines[j])
    f3.close()
    print('INFO: manifest.txt has been divided into validation.txt = %s%% and training.txt = %s%%' %
          (int(split*100), int(other_percentage*100)))
    # print(len(lines), len(lines_out), len(training_lines))


def updateYaml(classes, val, train, yml):
    names = [line.rstrip() for line in open(classes, 'r')]
    nc = len(names)
    data = {
        'train': train,
        'val': val,
        'nc': nc,
        'names': names
    }
    with open(yml, 'w') as f:
        yaml.dump(data, stream=f, default_flow_style=False, sort_keys=False)

    with open(yml, 'r') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        print('INFO: Classes: %s' % data['nc'])
        print('INFO: Classes are: %s' % data['names'])
        aux = yml.split('\\')[-1]
        print(f'INFO: {aux} updated')


if __name__ == "__main__":

    # Basic Parameters
    base_dataset = 'D:\\PyCharmProjects\\201_SeamsModel\\images\\train'  # path
    manifest = os.path.join(base_dataset, 'vott-manifest', 'manifest.txt')
    multi_df = pd.read_csv(os.path.join(base_dataset, 'vott-manifest', 'Seams-export.csv'))
    # Dataset split Parameters
    split_val = os.path.join(base_dataset, 'vott-manifest', 'validation.txt')
    split_train = os.path.join(base_dataset, 'vott-manifest', 'training.txt')
    classes_file = os.path.join(base_dataset, 'vott-manifest', 'classes.names')
    yaml_file = os.path.join(base_dataset, 'vott-manifest', "seams.yaml")  # yaml file location
    # Variables
    labels = multi_df["label"].unique()
    labeldict = dict(zip(labels, range(len(labels))))
    multi_df.drop_duplicates(subset=None, keep="first", inplace=True)

    # Calls
    manifest_generator(multi_df, manifest_target=manifest, path=base_dataset+'\\Seams')
    csv2darknet(multi_df, labeldict, path=base_dataset+'\\Seams')
    split_manifest(split=0.2, manifest_target=manifest, val=split_val, train=split_train)
    updateYaml(classes=classes_file, val=split_val, train=split_train, yml=yaml_file)
