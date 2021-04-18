import unittest
from tqdm import tqdm
from loguru import logger
from nlps_extraction.tasks.extraction import FixRedirectsTask, XMLParserTask
import random


class FixRedirectsTest(unittest.TestCase):
    def test_fix_redirect(self):
        parser = XMLParserTask()
        xml_file = parser.run()
        logger.info(random.choice(list(xml_file.values())))
        fix_redirect = FixRedirectsTask()
        fixed_result = fix_redirect.run(xml_file)

        for title, content in fixed_result.items():
            lower_content = content.lower()
            self.assertFalse("#redirect" in lower_content)

        logger.info(random.choice(list(fixed_result.values())))
        logger.info("Total of entries before removing redirects")
        logger.info(len(xml_file))

        logger.info("Total of entries after removing redirects")
        logger.info(len(fixed_result))
