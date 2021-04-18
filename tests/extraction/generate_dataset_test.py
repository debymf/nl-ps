import unittest
from tqdm import tqdm
from loguru import logger
from nlps_extraction.tasks.extraction import (
    FixRedirectsTask,
    XMLParserTask,
    FixSnippetsTask,
    GetCategoriesTask,
    CurateTitlesTask,
    GetDefinitionsTask,
    GetOthersTask,
    GenerateDatasetTask,
)
import random


class GetOthersTest(unittest.TestCase):
    def test_gen(self):

        xml_file = dict()
        fix_redirect = FixRedirectsTask()
        fixed_result = fix_redirect.run(xml_file)
        fix_snippets = FixSnippetsTask()
        fixed_snippets = fix_snippets.run(fixed_result)
        get_categories = GetCategoriesTask()
        out_entries = get_categories.run(fixed_snippets)
        curate_titles = CurateTitlesTask()
        curate_results = curate_titles.run(out_entries["out_entries"])
        get_definitions = GetDefinitionsTask()
        definitions = get_definitions.run(
            curate_results, out_entries["definitions_category"]
        )
        get_others = GetOthersTask()
        theorems = get_others.run(
            definitions["others"], out_entries["others_categories"]
        )
        logger.info("Number of Theorems:")
        logger.info(len(theorems["theorems"]))
        logger.info("Number of Lemmas:")
        logger.info(len(theorems["lemmas"]))
        logger.info("Number of Corollaries:")
        logger.info(len(theorems["corollaries"]))
        gen_task = GenerateDatasetTask()
        gen_task.run(
            definitions["definitions"],
            theorems["lemmas"],
            theorems["corollaries"],
            theorems["theorems"],
        )
