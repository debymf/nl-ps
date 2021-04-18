from prefect import Task
from dynaconf import settings
from typing import List, Tuple
from loguru import logger
from xml.etree import ElementTree as ET
from tqdm import tqdm

XML_FILE = settings["xml_input"]


class XMLParserTask(Task):
    def run(self):
        """Run XML parser"""
        logger.info("*** Starting XML Parsing ***")
        xml_file = dict()
        parser = ET.iterparse("data/wiki.xml")
        title = ""

        for event, element in tqdm(parser):
            # Title
            if "}title" in element.tag:
                title = str(element.text)
            # Content
            if "}text" in element.tag:
                text = str(element.text)
                xml_file[title] = text

        logger.success(f"Total statements in XML: {len(xml_file)}")

        return xml_file
