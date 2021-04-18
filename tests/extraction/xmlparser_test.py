import unittest
from tqdm import tqdm
from nlps_extraction.tasks.extraction import XMLParserTask
from loguru import logger


class XMLParserTest(unittest.TestCase):
    def test_xml_parsing(self):
        parser = XMLParserTask()
        xml_file = parser.run()
        self.assertIsNotNone(xml_file)
        logger.info(f"Total of entries in the XML file: {len(xml_file)}")
        logger.info("Sample xml file:")
        logger.info(list(xml_file.keys())[150])
        logger.info(xml_file[list(xml_file.keys())[150]])
