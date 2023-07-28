import os
import glob
import xml.etree.ElementTree as ET
import numpy as np


class CVATYoloConverter:
    def __init__(self, xml_path: str, classes_encoding: dict):
        self.xml_path_list: str = xml_path  # for the moment it is only one
        self.classes_encoding: dict = classes_encoding
        self.label: int = 0

    def get_image_annotation(self) -> None:
        """ XML in CVAT format to YOLO annotations """

        root = ET.parse(self.xml_path_list).getroot()
        meta = root.findall("image")

        for image in meta:
            image_name: str = str(image.attrib["name"])
            image_width: int = int(image.attrib["width"])
            image_height: int = int(image.attrib["height"])

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

                payload = [image_name, f'{self.label} {yolo_x} {yolo_y} {yolo_w} {yolo_h}']
                self.write_annotations_to_disk(payload)

    def classes_encoder(self, label) -> int:
        return self.classes_encoding[label]

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
        image_name: str = f'{payload[0].split(".")[0]}.txt'
        annotation_string: str = payload[1]
        with open(image_name, 'a') as f:
            f.write(f'{annotation_string}\n')


def main():
    xml_dir: str = 'annotations (2).xml'
    classes_encoding: dict = {
        'Seams': 0,
        'Beam': 1,
        'Souflure': 2,
        'Hole': 3,
        'Water': 4
    }

    convert = CVATYoloConverter(xml_dir, classes_encoding)
    convert.get_image_annotation()


if __name__ == '__main__':
    main()