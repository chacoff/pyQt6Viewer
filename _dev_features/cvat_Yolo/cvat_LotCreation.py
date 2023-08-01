import os
import shutil
import xml.etree.ElementTree as ET


def find_xml_files_recursive(_path: str):

    _xml_files: list = []
    for root, dirs, files in os.walk(_path):
        for file in files:
            if file.endswith('.xml'):
                _xml_files.append(os.path.join(root, file))
    return _xml_files


def main(_source: str, _annotations_xml: str):

    root = ET.parse(_annotations_xml).getroot()

    task = root.find('.//name')  # name of the file according the Lot << Infoscribe identification
    if task is not None:
        lot_name = task.text
        print("Name:", lot_name)

        meta = root.findall('image')
        for image in meta:
            image_name: str = str(image.attrib['name'])
            image_path: str = os.path.join(_source, lot_name)

            if not os.path.exists(image_path):
                os.makedirs(image_path)

            image_full_address_source = os.path.join(_source, image_name)
            image_full_address_target = os.path.join(image_path, image_name)

            try:
                shutil.move(image_full_address_source, image_full_address_target)
                # print(image_full_address_source, image_full_address_target)
            except FileNotFoundError as e:
                print(f'{image_name} doesnt exist, probably was already moved')
            finally:
                pass
                # print(f'Ok: {image_name}')


if __name__ == '__main__':
    # Parameters:
    source = f'C:\\Users\\gomezja\\PycharmProjects\\00_dataset\\Hole'
    infoscribe_hole = f'C:\\Users\\gomezja\\PycharmProjects\\00_dataset\\_Annotations_Infoscribe\\CVAT for images\\Hole'

    annotations_files = find_xml_files_recursive(infoscribe_hole)
    for xml_path in annotations_files:

        index = xml_path.split('\\')
        lot_xml = "\\".join(index[-2:])
        print(lot_xml)

        main(source, xml_path)
        shutil.move(os.path.join(infoscribe_hole, lot_xml), os.path.join(source, lot_xml))
