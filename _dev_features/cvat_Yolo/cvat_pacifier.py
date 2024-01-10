import os
import re
from xml.etree import ElementTree as ET
from collections import defaultdict


def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]


def count_images_and_xml(folder):
    png_count = 0
    bmp_count = 0
    jpg_count = 0
    xml_count = 0
    txt_count = 0
    xml_found = False

    for root, dirs, files in os.walk(folder):
        dirs.sort(key=natural_sort_key)  # Sort subfolders naturally
        for dir_name in dirs:
            if dir_name.startswith("Lot_"):
                lot_folder_path = os.path.join(root, dir_name)
                for file in os.listdir(lot_folder_path):
                    if file.endswith('.png'):
                        png_count += 1
                    elif file.endswith('.bmp'):
                        bmp_count += 1
                    elif file.endswith('.jpg'):
                        jpg_count += 1
                    elif file.endswith('.xml'):
                        xml_count += 1
                        xml_found = True
                    elif file.endswith('.txt'):
                        txt_count += 1

                if xml_found and (bmp_count+png_count+jpg_count) > txt_count:
                    print(f"Folder: {lot_folder_path}")
                    print(f"Total Images: {bmp_count + png_count + jpg_count}")
                    print(f"TXT annotations: {txt_count}")
                    print(f"XML file: {xml_count}")
                    print("-----------")
                elif xml_found:
                    pass
                    # print(f"Folder: {lot_folder_path}")
                    # print("XML OK and Images+annotations OK")
                    # print("-----------")
                else:
                    print(f"Folder: {lot_folder_path}")
                    print("XML file found: No")
                    print("-----------")

                png_count = 0
                bmp_count = 0
                jpg_count = 0
                xml_count = 0
                txt_count = 0
                xml_found = False


def find_duplicate_images(folder):
    image_name_paths = defaultdict(list)

    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith('.xml'):
                xml_path = os.path.join(root, file)
                tree = ET.parse(xml_path)
                root = tree.getroot()

                for image_elem in root.findall(".//image"):
                    image_name = image_elem.get("name")
                    image_name_paths[image_name].append(xml_path)

    for image_name, paths in image_name_paths.items():
        if len(paths) > 1:
            print(f"Image name: {image_name}, Count: {len(paths)}, Found in:")
            for path in paths:
                pat = os.path.join(*path.split('\\')[-2:])
                print(f"- {pat}")


def count_globals(folder):
    png_count = 0  #
    bmp_count = 0  # 10017
    jpg_count = 0
    xml_count = 0  # 509
    txt_count = 0  # 10017

    for root, dirs, files in os.walk(folder):
        for dir_name in dirs:
            lot_folder_path = os.path.join(root, dir_name)
            for file in os.listdir(lot_folder_path):
                if file.endswith('.png'):
                    png_count += 1
                elif file.endswith('.bmp'):
                    bmp_count += 1
                elif file.endswith('.jpg'):
                    jpg_count += 1
                elif file.endswith('.xml'):
                    xml_count += 1
                elif file.endswith('.txt'):
                    txt_count += 1

    print(f'globals: {[png_count+bmp_count+jpg_count]}, {xml_count}, {txt_count}')


if __name__ == "__main__":

    folder_path = r'C:\Users\AJMINO\Downloads\Dev\PySeamsDetection\Training\data\holes_dataset'
    # find_duplicate_images(folder_path)
    count_images_and_xml(folder_path)
    count_globals(folder_path)


