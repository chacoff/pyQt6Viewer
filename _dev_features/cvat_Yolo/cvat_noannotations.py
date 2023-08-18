import os
import shutil
from collections import Counter

def no_lot_seeker(folder: str):
    for file in os.listdir(folder):
        if file.endswith('.png'):
            print(file)
        elif file.endswith('.bmp'):
            print(file)
        elif file.endswith('.xml'):
            pass


def count_images(folder_path, extensions):
    bmp_count = 0
    png_count = 0

    for root, _, files in os.walk(folder_path):
        for file in files:
            _, ext = os.path.splitext(file)
            if ext.lower() in extensions:
                if ext.lower() == ".bmp":
                    bmp_count += 1
                elif ext.lower() == ".png":
                    png_count += 1

    return bmp_count, png_count


def find_and_copy_missing_images(uploaded_folder, dataset_folder, missing_folder):
    uploaded_images = get_image_list_recursive(uploaded_folder)
    print(f'uploaded: {len(uploaded_images)}')
    dataset_images = get_image_list_recursive(dataset_folder)
    print(f'dataset: {len(dataset_images)}')

    missing_images = [x for x in uploaded_images if x not in dataset_images]
    print(f'missing: {len(missing_images)}')

    duplicate_items = find_duplicates(uploaded_images)
    print(len(duplicate_items))

    # for image_path in missing_images:
    #     source_image_path = os.path.join(uploaded_folder, image_path)
    #     missing_image_path = os.path.join(missing_folder, image_path)
    #
    #     # Create necessary folders in the missing directory
    #     missing_image_folder = os.path.dirname(missing_image_path)
    #     os.makedirs(missing_image_folder, exist_ok=True)
    #
    #     print(f"Copying missing image {image_path} to missing folder.")
    #     # shutil.copy(source_image_path, missing_image_path)


def get_image_list_recursive(folder):
    image_list = []
    for root, _, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(('.png', '.bmp')):
                image_list.append(os.path.join(file))
    return image_list


def find_duplicates(lst):
    counter = Counter(lst)
    duplicates = [item for item, count in counter.items() if count > 1]
    return duplicates


if __name__ == '__main__':

    uploaded = r'C:\Users\gomezja\PycharmProjects\00_dataset\training_uploaded'
    dataset = r'C:\Users\gomezja\PycharmProjects\00_dataset\training'
    missing = r'C:\Users\gomezja\PycharmProjects\00_dataset\training\missing'
    extensions = [".bmp", ".png"]

    bmp_count, png_count = count_images(dataset, extensions)
    print(f"Number of BMP images: {bmp_count}\nNumber of PNG images: {png_count}")

    find_and_copy_missing_images(uploaded, dataset, missing)

