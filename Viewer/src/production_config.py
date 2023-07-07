import xml.etree.ElementTree as ET


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


def main():
    pass


if __name__ == '__main__':
    # usage

    xml_file_path = "production_config.xml"
    config = XMLConfig(xml_file_path)
    lista = config.get_value('Production', 'profile_not_of_interest')

