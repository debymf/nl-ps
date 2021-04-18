import unittest
from tqdm import tqdm
from loguru import logger
from nlps_extraction.tasks.extraction import (
    FixRedirectsTask,
    XMLParserTask,
    FixSnippetsTask,
    GetCategoriesTask,
    CurateTitlesTask,
)
import random


class CurateTitlesTest(unittest.TestCase):
    def test_curate_titles(self):
        parser = XMLParserTask()
        xml_file = parser.run()

        fix_redirect = FixRedirectsTask()
        fixed_result = fix_redirect.run(xml_file)

        fix_snippets = FixSnippetsTask()
        fixed_snippets = fix_snippets.run(fixed_result)
        get_categories = GetCategoriesTask()
        out_entries = get_categories.run(fixed_snippets)
        curate_titles = CurateTitlesTask()
        logger.info("Before curation")
        logger.info(len(out_entries["out_entries"]))
        logger.info("After curation")
        curate_results = curate_titles.run(out_entries["out_entries"])
        logger.info(len(curate_results))
