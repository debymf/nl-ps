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
    GenerateOutputTask,
)
import random


class GenerateOutputTest(unittest.TestCase):
    def test_generate_output(self):
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
        generate_output = GenerateOutputTask()

        (
            out_definitions,
            out_lemmas,
            out_theorems,
            out_corollaries,
        ) = generate_output.run(definitions, lemmas, corollaries, theorems)
