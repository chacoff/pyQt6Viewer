import xml.etree.ElementTree as ET
from PyQt6.QtGui import QColor

class XMLConfig:
    def __init__(self, xml_path):
        self.xml_path = xml_path
        self.tree = None
        self.root = None

    def get_value(self, group, parameter):
        if self.tree is None:
            self.tree = ET.parse(self.xml_path)
            self.root = self.tree.getroot()

        xpath = f"./{group}/{parameter}"
        element = self.root.find(xpath)
        if element is not None:
            return element.text
        else:
            raise ValueError(f"Parameter '{parameter}' in group '{group}' not found.")

    def get_classes(self, group, defect, parameter):
        if self.tree is None:
            self.tree = ET.parse(self.xml_path)
            self.root = self.tree.getroot()

        xpath = f"./{group}/{defect}/{parameter}"
        element = self.root.find(xpath)
        if element is not None:
            return element.text
        else:
            raise ValueError(f"Parameter '{parameter}' in group '{group}' not found.")

    def get_classes_colors_thres(self):
        if self.tree is None:
            self.tree = ET.parse(self.xml_path)
            self.root = self.tree.getroot()

        class_data = []
        for class_elem in self.root.findall('Classes/*'):
            class_name = class_elem.tag
            confidence = float(class_elem.find('confidence').text)
            color_data = class_elem.find('color').text
            color = QColor(*map(int, color_data.split(';')))
            class_data.append((class_name, color, f' {confidence * 100:.1f}'))

        return class_data


def main():
    pass


if __name__ == '__main__':
    # usage

    xml_file_path = "production_config.xml"
    config = XMLConfig(xml_file_path)
    lista = config.get_value('Production', 'profile_not_of_interest')
    classes = config.get_classes('Classes', 'Seams', 'color')
    all = config.get_classes_colors_thres()
    print(all)

