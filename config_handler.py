import xml.etree.ElementTree as ET


def getvar(file_path: str, key: str) -> str:
    root = ET.parse(file_path).getroot()

    for string in root.findall('variable'):
        if string.get('name') == key:
            return string.text

    raise Exception('No value was found by the key!')
