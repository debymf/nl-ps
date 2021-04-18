import unittest
from tqdm import tqdm
from loguru import logger
from nlps_extraction.tasks.extraction import (
    FixRedirectsTask,
    XMLParserTask,
    FixSnippetsTask,
)
import random


class FixSnippetsTest(unittest.TestCase):
    def test_fix_snippets(self):
        parser = XMLParserTask()
        xml_file = parser.run()
        fix_redirect = FixRedirectsTask()
        fixed_result = fix_redirect.run(xml_file)
        fix_snippets = FixSnippetsTask()
        fixed_snippets = fix_snippets.run(fixed_result)
        title, content = random.choice(list(fixed_snippets.items()))
        logger.info(title)
        logger.info(content)
