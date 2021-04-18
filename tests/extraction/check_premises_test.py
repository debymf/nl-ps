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
    CheckPremisesTask,
)
import random


class CheckPremisesTest(unittest.TestCase):
    def test_check_pemises(self):
        parser = XMLParserTask()
        xml_file = parser.run()
        fix_redirect = FixRedirectsTask()
        fixed_result = fix_redirect.run(xml_file)
        fix_snippets = FixSnippetsTask()
        fixed_snippets = fix_snippets.run(fixed_result)
        get_categories = GetCategoriesTask()
        out_entries, definitions_category, others_categories = get_categories.run(
            fixed_snippets
        )
        curate_titles = CurateTitlesTask()
        curate_results = curate_titles.run(out_entries)
        get_definitions = GetDefinitionsTask()
        definitions, others = get_definitions.run(curate_results, definitions_category)
        get_others = GetOthersTask()
        theorems, lemmas, corollaries = get_others.run(others, others_categories)
        check_premises = CheckPremisesTask()
        lemmas, corollaries, theorems = check_premises.run(
            definitions, lemmas, corollaries, theorems
        )
        logger.info("Number of Definitions:")
        logger.info(len(definitions))
        logger.info("Number of Theorems:")
        logger.info(len(theorems))
        logger.info("Number of Lemmas:")
        logger.info(len(lemmas))
        logger.info("Number of Corollaries:")
        logger.info(len(corollaries))

        title_t, content_t = random.choice(list(theorems.items()))
        title_l, content_l = random.choice(list(lemmas.items()))
        title_c, content_c = random.choice(list(corollaries.items()))
        title_d, content_d = random.choice(list(definitions.items()))
