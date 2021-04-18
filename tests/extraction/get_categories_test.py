import unittest
from tqdm import tqdm
from loguru import logger
from nlps_extraction.tasks.extraction import (
    FixRedirectsTask,
    XMLParserTask,
    FixSnippetsTask,
    GetCategoriesTask,
)
import random


class GetCategoriesTest(unittest.TestCase):
    def test_categories(self):
        parser = XMLParserTask()
        xml_file = parser.run()
        fix_redirect = FixRedirectsTask()
        fixed_result = fix_redirect.run(xml_file)
        fix_snippets = FixSnippetsTask()
        fixed_snippets = fix_snippets.run(fixed_result)
        get_categories = GetCategoriesTask()
        out_entries, definitions_category, top_categories = get_categories.run(
            fixed_snippets
        )
