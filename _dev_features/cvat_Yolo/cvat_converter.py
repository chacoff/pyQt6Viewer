import os
import glob
import xml.etree.ElementTree as ET
import numpy as np
import time


class CVATYoloConverter:
    def __init__(self, xml_path: str, classes_encoding: dict):
        self.xml_path_list: str = xml_path  # for the moment it is only one
        self.classes_encoding: dict = classes_encoding
        self.label: int = 0

    def get_image_annotation(self, _xml_file: str) -> None:
        """ XML in CVAT format to YOLO annotations """

        rel_path = os.path.dirname(_xml_file)

        root = ET.parse(_xml_file).getroot()
        meta = root.findall("image")

        for image in meta:
            image_name: str = str(image.attrib["name"])
            image_width: int = int(image.attrib["width"])
            image_height: int = int(image.attrib["height"])

            full_image_name = os.path.join(rel_path, image_name)

            if os.path.isfile(full_image_name):
                object_metas = image.findall("polygon")
                for bbox in object_metas:
                    label = bbox.attrib['label']
                    self.label = self.classes_encoder(label)
                    points = bbox.attrib['points'].split(';')

                    points_array = self.points_to_points_array(points)

                    tl = [min(points_array[:, 0]), min(points_array[:, 1])]  # TOP-LEFT
                    br = [max(points_array[:, 0]), max(points_array[:, 1])]  # BOTTOM-RIGHT

                    xtl = tl[0]
                    ytl = tl[1]
                    xbr = br[0]
                    ybr = br[1]

                    yolo_x = round(((xtl + xbr) / 2) / image_width, 6)
                    yolo_y = round(((ytl + ybr) / 2) / image_height, 6)
                    yolo_w = round((xbr - xtl) / image_width, 6)
                    yolo_h = round((ybr - ytl) / image_height, 6)

                    payload = [full_image_name, f'{self.label} {yolo_x} {yolo_y} {yolo_w} {yolo_h}']
                    self.write_annotations_to_disk(payload)

    def classes_encoder(self, label) -> int:
        return self.classes_encoding[label]

    def find_xml_files_recursive(self) -> list:
        _xml_files: list = []
        for root, dirs, files in os.walk(self.xml_path_list):
            for file in files:
                if file.endswith('.xml'):
                    _xml_files.append(os.path.join(root, file))
        return _xml_files

    @staticmethod
    def points_to_points_array(points) -> np.array:
        """ CVAT polygons to a numpy array """
        points_array = np.empty((len(points), 2), dtype=np.float64)

        for i, point_str in enumerate(points):
            x_str, y_str = point_str.split(',')
            x = float(x_str)
            y = float(y_str)
            points_array[i] = [x, y]

        points_array = np.array(points_array)

        return points_array

    @staticmethod
    def write_annotations_to_disk(payload: list) -> None:
        annotation_name: str = f'{payload[0].split(".")[0]}.txt'
        annotation_string: str = payload[1]
        
        # with open(annotation_name, 'a') as f:
        #     f.write(f'{annotation_string}\n')

        f = open(annotation_name, 'a')
        f.write(f'{annotation_string}\n')
        f.close()
        time.sleep(0.005)


def main():
    xml_dir: str = r'C:\Users\gomezja\PycharmProjects\00_dataset\training'

    classes_encoding: dict = {
        'Seams': 0,
        'Beam': 1,
        'Souflure': 2,
        'Hole': 3,
        'Water': 4
    }

    convert = CVATYoloConverter(xml_dir, classes_encoding)
    xmls = convert.find_xml_files_recursive()

    i = 0
    for xml in xmls:
        print(xml)
        convert.get_image_annotation(xml)
        i += 1
    print(f'found {i} annotations.xml')


if __name__ == '__main__':
    main()