from prefect import Task
from dynaconf import settings
from loguru import logger
from tqdm import tqdm
from collections import Counter
import regex as re
from nlps_extraction.util.caching import recover_cache, save_cache
import sys

CACHE_LOCATION = "./cache/definitions_cache.msgpack"


class GetDefinitionsTask(Task):
    def run(self, entries, definitions_category, use_cache=True):
        logger.info("Getting definitions")
        others = dict()
        definitions = dict()
        for title, content in entries.items():
            if "definition:" in title.lower():
                definitions[title] = content
            else:
                others[title] = content

        logger.info("Found definitions:")
        logger.info(len(definitions))

        all_statements = list()
        all_titles = list()
        parsed_definitions = dict()
        all_categories = list()
        for title, content in definitions.items():
            content = (
                content.replace("<onlyinclude>", "")
                .replace("</onlyinclude>", "")
                .replace("<includeonly>", "")
                .replace("</includeonly>", "")
            )
            statement = self.get_definition_statement(content)
            if statement.replace(
                "== Definition ==", ""
            ).strip() and self.check_def_blacklist(statement):
                all_statements.append(statement)
                all_titles.append(title)
                categories, categories_replace = self.get_category_from_entry(content)
                this_categories = list()
                for c in categories:
                    if c in definitions_category:
                        all_categories.extend(definitions_category[c])
                        this_categories.extend(definitions_category[c])
                    else:
                        this_categories.append(c)
                for c in categories_replace:
                    statement = statement.replace(c, "")
                parsed_definitions[title] = [this_categories, statement]

        top_cat = Counter(all_categories).most_common(30)

        top_categories = list()
        for t in top_cat:
            if t[0] and "logic" not in t[0].lower():
                top_categories.append(t[0])
        print(top_categories)

        filtered_definitions = dict()

        for title, element in parsed_definitions.items():
            cat = element[0]
            for t in top_categories:
                if t in cat:
                    if t == " Topology (Mathematical Branch)":
                        filtered_definitions[title] = ["Topology", element[1]]
                    else:
                        filtered_definitions[title] = [t.strip(), element[1]]

        parsed_definitions = filtered_definitions
        print(len(filtered_definitions))

        selected_definitions = dict()

        all_statements = list()
        all_titles2 = list()
        for title, element in parsed_definitions.items():
            if "{{:" not in element[1]:
                selected_definitions[title] = element
                all_statements.append(element[1])
                all_titles2.append(title)

        print(len(selected_definitions))

        new_selected_definitions = dict()
        all_statements = list()
        all_statements = []
        for title, element in selected_definitions.items():
            sections = re.findall(r"(==+ *.+? *==+) *[\r\n]+", element[1])
            content = element[1]
            for s in sections:
                content = content.replace(s, "")
            premises = self.get_premises(content)
            regex_exp = r"\[\[[^\|\]]*\|*.*?\]\]"
            matches = re.findall(regex_exp, content)
            for m in matches:
                to_replace = m.replace("[[", "").replace("]]", "")
                if "|" in to_replace:
                    to_replace = to_replace.split("|")[1]
                if "Definition:" in to_replace:
                    to_replace = to_replace.replace("Definition:", "")
                content = content.replace(m, to_replace)
            new_selected_definitions[title] = [element[0], content, list(set(premises))]

            all_statements.append(content)

        all_titles = list()

        for title, element in new_selected_definitions.items():
            all_titles.append(title)

        definitions = dict()

        for title, element in new_selected_definitions.items():
            category = element[0]
            content = element[1]
            premises = element[2]
            new_premises = list()
            for p in premises:
                if p in all_titles:
                    new_premises.append(p)
            definitions[title] = [category, content, premises]

        results = {"definitions": definitions, "others": others}

        return results

    def check_def_blacklist(self, content):
        REMOVE = [
            "{{mergeto|",
            "{{refactor",
            "{{confuse|",
            "{{missinglinks",
            "{{about|",
            "{{rename|",
            "{{tidy",
            "{{explain",
            "{{delete",
            "{{stub",
            "{{Proofread}}",
        ]
        for r in REMOVE:
            if r in content.lower():
                return False
        return True

    def get_category_from_entry(self, content):
        regex_exp = r"\[\[(Category:[^\|\]]*)\|*.*\]\]"
        regex_replace = r"\[\[Category:[^\|\]]*\|*.*\]\]"
        matches = re.findall(regex_exp, content)
        matches2 = re.findall(regex_replace, content)

        return matches, matches2

    def get_definition_statement(self, text):
        FILTERED_SECTIONS = [
            "Also see",
            "Sources",
            "Mistake",
            "Also known as",
            "Historical Note",
            "Generalization",
            "Notes",
            "Linguistic Note",
            "Note",
            "References",
            "Examples",
            "Comment",
            "Fallacy",
        ]
        clean_entries = list()
        i = 0
        new_text = ""
        sections = re.findall(r"(==+ *.+? *==+) *[\r\n]+", text)

        if sections:
            sections_regex = ""
            for section in sections:
                sections_regex = sections_regex + "|" + re.escape(section)
            sections_regex = sections_regex[1:]
            sections_content = re.split(sections_regex, text)
            if sections_content[0] == "":
                sections_content = sections_content[1:]
            selected_sections = []
            selected_content = []
            i = 0
            new_text = ""
            for section in sections:
                found = 0
                for word in FILTERED_SECTIONS:
                    if word.lower() in section.lower():
                        found = 1
                if found == 0:
                    if "definition" in section.lower():
                        new_text = (
                            new_text
                            + "\n"
                            + section
                            + "\n"
                            + sections_content[i]
                            + "\n"
                        )
                        selected_sections.append(section)
                        selected_content.append(sections_content[i])

                i = i + 1

        return new_text

    def get_premises(self, content):
        premises = list()
        regex_exp = r"\[\[([^\|\]]*)\|*.*\]\]"
        matches = re.findall(regex_exp, content)
        for m in matches:
            if "Category:" not in m and "File:" not in m:
                premises.append(m)

        return premises
