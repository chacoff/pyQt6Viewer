"""
ManifestGenerator to YOLOv5-Seams
April 10 2023
J.
"""

import os
import pandas as pd
from tqdm import tqdm
import yaml
import numpy as np
from numpy.random import seed
from numpy.random import randint
import shutil


def manifest_generator(param):

    total_lists = []
    for clas in param.get('folder_class'):
        path = os.path.join(param.get('base'), clas)
        list_per_folder = [x for x in os.listdir(path) if x.endswith(param.get('image_filter'))]
        complete_list = [clas+'\\' + x for x in list_per_folder]
        total_lists.append(complete_list)

    images_name = sum(total_lists, [])
    manifest = os.path.join(param.get('base'), param.get('manifest'))

    pbar = tqdm(total=len(images_name))
    for i in range(len(images_name)):
        file = open(manifest, 'a+')
        image_i = str(os.path.join(param.get('base'), images_name[i]))
        file.write(image_i+'\n')
        file.close()
        pbar.update(1)
    pbar.close()
    print('INFO: Total number of images: %s' % len(images_name))


def split_manifest(param):
    manifest = os.path.join(param.get('base'), param.get('manifest'))
    manifest_validation = os.path.join(param.get('base'), param.get('manifest_validation'))
    manifest_training = os.path.join(param.get('base'), param.get('manifest_training'))

    other_percentage = 1 - param.get('split')

    f = open(manifest, 'r')  # manifest.txt, a list with all the images
    lines = f.readlines()
    f.close()

    np.random.shuffle(lines)

    total_lines = len(lines)
    num_val = int(param.get('split') * total_lines)
    num_train = int(total_lines - num_val)

    seed(5)
    lines_out = []  # list with the lines that will be removed later
    random_line = randint(0, total_lines, num_val)  # Vector with all the images (lines) we will use for validation
    #  print(random_line)
    f2 = open(manifest_validation, 'a+')
    for i in range(num_val):
        f2.writelines(lines[random_line[i]])
        lines_out.append(lines[random_line[i]])
    f2.close()

    training_lines = [x for x in lines if x not in lines_out]  # removed the lines_out from lines = full manifest here
    f3 = open(manifest_training, 'a+')
    for j in range(num_train):
        f3.writelines(training_lines[j])
    f3.close()
    print('INFO: manifest.txt has been divided into validation.txt = %s%% and training.txt = %s%%' %
          (int(param.get('split')*100), int(other_percentage*100)))


def updateYaml(param):
    yml = os.path.join(param.get('base'), param.get('yml'))
    # names = [line.rstrip() for line in open(classes, 'r')]

    data = {
        'train': os.path.join(param.get('base'), param.get('manifest_training')),
        'val': os.path.join(param.get('base'), param.get('manifest_validation')),
        'nc': len(param.get('classes')),
        'names': param.get('classes')
    }
    with open(yml, 'w') as f:
        yaml.dump(data, stream=f, default_flow_style=False, sort_keys=False)

    with open(yml, 'r') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        print('INFO: Classes are: %s' % data['names'])
        aux = yml.split('\\')[-1]
        print(f'INFO: {aux} updated')


def mover(param):
    path = param.get('base')+param.get('train')
    dst = param.get('base')+param.get('destination')
    images_name = [x for x in os.listdir(path) if x.endswith(param.get('annotation_filter'))]

    pbar = tqdm(total=len(images_name))
    for i in range(len(images_name)):
        single_txt_source = os.path.join(path, images_name[i])
        single_image_source = os.path.join(path, images_name[i]).split('.')[0] + '.bmp'
        single_txt_dst = os.path.join(dst, images_name[i])
        single_image_dst = os.path.join(dst, images_name[i]).split('.')[0] + '.bmp'

        shutil.move(single_txt_source, single_txt_dst)
        shutil.move(single_image_source, single_image_dst)

        pbar.update(1)
    pbar.close()
    print('INFO: Total number of images: %s' % len(images_name))


if __name__ == "__main__":
    parameters = {
        'base': 'F:\\00_Seams\\dataset',
        'folder_class': ['Seams', 'Hole'],
        'destination': 'Reference',
        'manifest': 'manifest.txt',
        'manifest_validation': 'validation.txt',
        'manifest_training': 'training.txt',
        'image_filter': '.bmp',
        'annotation_filter': '.txt',
        'split': 0.20,
        'classes': ['Seams', 'Beam', 'Souflure', 'Hole', 'Water'],
        'yml': 'seams.yaml'
    }

    # mover(parameters)
    manifest_generator(parameters)
    split_manifest(parameters)
    updateYaml(parameters)
