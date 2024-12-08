import os.path
import xml.etree.ElementTree as ET


def getvar(key: str, *file_paths: str) -> str:
    for fp in file_paths:
        if not os.path.exists(fp):
            continue

        root = ET.parse(fp).getroot()

        for string in root.findall('variable'):
            if string.get('name') == key:
                return string.text

        raise Exception('No value was found by the key!')

    raise IOError("All provided paths do not exist!")
