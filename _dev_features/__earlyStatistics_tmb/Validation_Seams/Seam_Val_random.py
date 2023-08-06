import random
from pathlib import Path
import csv
import pandas as pd
import os
import shutil
from tqdm import tqdm
from time import sleep


def main(path, extension):
    return Path(path).glob(extension)


def random_generator(bmp_files, global_address, copy=True):

    def n_total_images():
        bmp_list = []
        for file in bmp_files:
            bmp_list.append(file)
        print(f'images: {len(bmp_list)}')

        return bmp_list

    list_images = n_total_images()

    sample_list = []
    pbar = tqdm(total=n_sample)
    for i in range(n_sample):
        li = range(1, len(list_images))
        rand_idx = random.sample(li, 1)[0]  # random.randrange(len(list_images))
        random_image = list_images[rand_idx]
        sample_list.append(random_image)
        if copy:
            random_image_name = random_image.__str__().split('\\')[-1]
            random_image_dest = os.path.join(global_address, random_image_name)
            shutil.copy(random_image, random_image_dest)
            sleep(0.1)
        pbar.update(1)
    pbar.close()

    print(f'sample: {len(sample_list)}')

    dictio = {'Location': sample_list}
    df = pd.DataFrame(dictio)
    df = df.drop_duplicates(keep='first')  # due to duplicate in the random numbers, i.e., copying twice the same image
    df.to_csv(f'sample_list_{df.shape[0]}_total{len(list_images)}.csv')


if __name__ == '__main__':
    # parameters
    path = f'S:\\defects\\ZH022\\2420'
    # path = f'C:\\Users\\gomezja\\PycharmProjects\\Tmb\\Validation_Seams\\Validation03_2022_10_26'
    n_sample = 1100
    extension = '*.bmp'
    copy = True
    global_address = 'C:\\Users\\gomezja\\PycharmProjects\\Tmb\\Validation_Seams\\Validation03_2022_10_26'

    bmp_files_list = main(path, extension)
    random_generator(bmp_files_list, global_address, copy)


