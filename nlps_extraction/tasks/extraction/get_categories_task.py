from prefect import Task
from dynaconf import settings
from loguru import logger
from tqdm import tqdm
import regex as re

CACHE_LOCATION = "./cache/categories_cache.msgpack"


class GetCategoriesTask(Task):
    def run(self, entries_dict):
        logger.info("Starting getting categories")

        xml_dict = dict()
        cat_dict = dict()
        cat_def_dict = dict()

        ## There are categories for definitions and for
        for title, content in entries_dict.items():
            if "Category:" in title:
                if "Category:Definitions" in title:
                    cat_def_dict[title] = content
                else:
                    cat_dict[title] = content
            else:
                xml_dict[title] = content

        definitions_category = dict()
        ### Definitions categories
        regex = r"(\{\{DefinitionCategory\|def \= .*? \}\})"
        for title, content in cat_def_dict.items():
            if "{{DefinitionCategory|def" in content:
                line = content.split("}}")[0]
                if "{{DefinitionCategory|def =" in line:
                    line = line.split("{{DefinitionCategory|def =")[1]
                else:
                    line = line.split("{{DefinitionCategory|def=")[1]
                if "|" in line:
                    line = line.split("|")
                else:
                    line = [line.strip()]
                definitions_category[title] = line

            elif "{{DefinitionCategory|disp" in content:
                line = content.split("}}")[0]
                line = line.split("{{DefinitionCategory|disp =")[1]
                line = line.split("|")[-1]
                definitions_category[title] = [line.strip()]
            elif "{{DefinitionCategory|" in content:
                line = content.split("}}")[0]
                line = line.split("{{DefinitionCategory|")[1]
                if "|" in line:
                    line = line.split("|")
                else:
                    line = [line.strip()]
                definitions_category[title] = line

        regex = r"\[\[(Category:[^\|\]]*)\|*.*\]\]"
        categories_topology_dict = dict()
        connected_categories_dict = dict()

        elementary_categories = list()

        ### Get all categories and top categories
        for title, content in cat_dict.items():
            matches = re.findall(regex, content)
            connected_categories_dict[title] = matches

        ### Get all categories and sub categories
        for title, categories in connected_categories_dict.items():
            for c in categories:
                if c not in categories_topology_dict:
                    categories_topology_dict[c] = []

                categories_topology_dict[c].append(title)
        # elementary_categories.extend(categories_topology_dict["Category:Definitions by Topic"])
        elementary_categories.extend(
            categories_topology_dict["Category:Proofs by Topic"]
        )
        elementary_categories.extend(categories_topology_dict["Category:Axioms"])
        elementary_categories.extend(categories_topology_dict["Category:Examples"])

        logger.info("Elementary Categories")
        logger.info(len(elementary_categories))

        top_categories = dict()

        for e in elementary_categories:
            top_categories[e] = []
            if e in categories_topology_dict:
                top_categories[e] = self.get_all_categories(
                    categories_topology_dict[e], categories_topology_dict
                )
                logger.info(e)
                logger.info(len(top_categories[e]))

        results = {
            "out_entries": xml_dict,
            "definitions_category": definitions_category,
            "others_categories": top_categories,
        }

        return results

    def get_all_categories(self, categories, categories_topology_dict):
        to_visit = []
        to_visit.extend(categories)
        visited = list()

        while len(to_visit) > 0:
            next_cat = to_visit.pop()
            visited.append(next_cat)

            if next_cat in categories_topology_dict:
                for c in categories_topology_dict[next_cat]:
                    if c not in visited:
                        to_visit.append(c)
        return list(set(visited))
