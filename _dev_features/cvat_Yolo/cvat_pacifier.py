import os
import re


def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]


def count_images_and_xml(folder):
    png_count = 0
    bmp_count = 0
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
                    elif file.endswith('.xml'):
                        xml_found = True

                if xml_found:
                    print(f"Folder: {lot_folder_path}")
                    print(f"Number of PNG images: {png_count}")
                    print(f"Number of BMP images: {bmp_count}")
                    print("XML file found: Yes")
                    print("-----------")
                else:
                    print(f"Folder: {lot_folder_path}")
                    print("XML file found: No")
                    print("-----------")

                png_count = 0
                bmp_count = 0
                xml_found = False


if __name__ == "__main__":
    folder_path = r'C:\Users\gomezja\PycharmProjects\00_dataset\training'
    count_images_and_xml(folder_path)
