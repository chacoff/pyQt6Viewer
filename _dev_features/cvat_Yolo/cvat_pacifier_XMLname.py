import os
from xml.etree import ElementTree as ET
from collections import defaultdict


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


if __name__ == "__main__":
    folder_path = r'C:\Users\gomezja\PycharmProjects\00_dataset\training'
    find_duplicate_images(folder_path)
