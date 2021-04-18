from prefect import Task
from dynaconf import settings
from loguru import logger
from tqdm import tqdm
import regex as re

FILTERED_CATEGORIES = [
    "Analysis",
    "Set Theory",
    "Number Theory",
    "Abstract Algebra",
    "Topology",
    "Algebra",
    "Relation Theory",
    "Mapping Theory",
    "Real Analysis",
    "Geometry",
    "Metric Spaces",
    "Linear Algebra",
    "Complex Analysis",
    "Applied Mathematics",
    "Order Theory",
    "Numbers",
    "Physics",
    "Group Theory",
    "Ring Theory",
    "Euclidean Geometry",
    "Class Theory",
    "Discrete Mathematics",
    "Plane Geometry",
    "Units of Measurement",
]


class GetOthersTask(Task):
    def run(self, others, others_categories):
        categories_decoder = dict()
        for title, elements in others_categories.items():
            categories_decoder[title] = title
            for e in elements:
                categories_decoder[e] = title

        tmp_others = dict()
        print(len(others))
        for title, element in others.items():
            categories, categories_replace = self.get_category_from_entry(element)
            for c in categories:
                for f in FILTERED_CATEGORIES:
                    if c in categories_decoder:
                        real_category = categories_decoder[c]
                        if f.lower() in real_category.lower():
                            category = f
                            tmp_others[title] = [category, element]
                            break

        filtered_others = dict()
        theorems = dict()
        lemmas = dict()
        corollaries = dict()
        lem = 0
        cor = 0
        theo = 0

        for title, element in tmp_others.items():
            category = element[0]
            text, sections, content = self.get_sections(element[1])

            for s in sections:
                if "theorem" in title.lower():
                    result = self.get_theorem(text, sections, content)
                    if result:
                        theorems[title] = [category] + result
                    break
                elif "lemma" in title.lower():
                    result = self.get_lemma(text, sections, content)
                    if result:
                        lemmas[title] = [category] + result
                    break
                elif "corollar" in title.lower():
                    result = self.get_corollary(text, sections, content)
                    if result:
                        corollaries[title] = [category] + result
                    break
                elif "theorem" in s.lower():
                    result = self.get_theorem(text, sections, content)
                    if result:
                        theorems[title] = [category] + result
                    break
                elif "lemma" in s.lower():
                    result = self.get_lemma(text, sections, content)
                    if result:
                        lemmas[title] = [category] + result
                    break
                elif "corollary" in s.lower():
                    result = self.get_corollary(text, sections, content)
                    if result:
                        corollaries[title] = [category] + result
                    break

        return {"theorems": theorems, "lemmas": lemmas, "corollaries": corollaries}

    def get_sections(self, text):
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

        selected_sections = list()
        selected_content = list()
        sections_content = list()
        new_text = ""
        sections = re.findall(r"(==+ *.+? *==+) *[\r\n]+", text)
        if sections:
            sections_regex = ""
            for section in sections:
                sections_regex = sections_regex + "|" + re.escape(section)
            sections_regex = sections_regex[1:]
            sections_content = re.split(sections_regex, text)
            if sections_content[0].strip() == "":
                sections_content = sections_content[1:]
            if len(sections_content) > len(sections):
                new_sections = list()
                new_sections.append("None")
                new_sections.extend(sections)
                sections = new_sections
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

        return new_text, sections, sections_content

    def get_category_from_entry(self, content):
        regex_exp = r"\[\[(Category:[^\|\]]*)\|*.*\]\]"
        regex_replace = r"\[\[Category:[^\|\]]*\|*.*\]\]"
        matches = re.findall(regex_exp, content)
        matches2 = re.findall(regex_replace, content)

        return matches, matches2

    def get_premises(self, content):
        premises = list()
        regex_exp = r"\[\[([^\|\]]*)\|*.*\]\]"
        matches = re.findall(regex_exp, content)
        for m in matches:
            if "Category:" not in m and "File:" not in m:
                premises.append(m)

        return list(set(premises))

    def get_definitions(self, content):
        premises = list()
        regex_exp = r"\[\[([^\|\]]*)\|*.*\]\]"
        matches = re.findall(regex_exp, content)
        for m in matches:
            if "Definition:" in m:
                premises.append(m)

        return list(set(premises))

    def replace_refs(self, content):
        regex_exp = r"\[\[[^\|\]]*\|*.*?\]\]"
        matches = re.findall(regex_exp, content)
        for m in matches:
            to_replace = m.replace("[[", "").replace("]]", "")
            if "|" in to_replace:
                to_replace = to_replace.split("|")[1]
            if "Definition:" in to_replace:
                to_replace = to_replace.replace("Definition:", "")
            content = content.replace(m, to_replace)
        return content

    def get_theorem(self, text, sections, sections_content):
        proofs = list()
        theorem_content = ""
        all_premises = list()
        for i in range(0, len(sections)):
            if "theorem" in sections[i].lower() and "proof" not in sections[i].lower():
                theorem_content = theorem_content + "\n\n" + sections_content[i]
            elif "proof" in sections[i].lower():
                if "{{:" not in sections_content[i]:
                    proofs.append(self.replace_refs(sections_content[i]))
                    premises = self.get_premises(sections_content[i])
                    all_premises.extend(premises)

            theorem_content_def = self.get_definitions(theorem_content)
            theorem_content = self.replace_refs(theorem_content)
        if (
            len(proofs) > 0
            and len(theorem_content.strip()) > 0
            and "{{:" not in theorem_content
        ):
            return [theorem_content, proofs, all_premises]
        else:
            return []

    def get_lemma(self, text, sections, sections_content):
        proofs = list()
        theorem_content = ""
        all_premises = list()
        for i in range(0, len(sections)):
            if (
                "theorem" in sections[i].lower() or "lemma" in sections[i].lower()
            ) and "proof" not in sections[i].lower():
                theorem_content = theorem_content + "\n\n" + sections_content[i]
            elif "proof" in sections[i].lower():
                if "{{:" not in sections_content[i]:
                    proofs.append(self.replace_refs(sections_content[i]))
                    premises = self.get_premises(sections_content[i])
                    all_premises.extend(premises)
            theorem_content_def = self.get_definitions(theorem_content)
            theorem_content = self.replace_refs(theorem_content)
        if (
            len(proofs) > 0
            and len(theorem_content.strip()) > 0
            and "{{:" not in theorem_content
        ):
            return [theorem_content, proofs, all_premises]
        else:
            return []

    def get_corollary(self, text, sections, sections_content):
        proofs = list()
        theorem_content = ""
        corollary_to = ""
        all_premises = list()
        for i in range(0, len(sections)):
            if (
                "theorem" in sections[i].lower() or "coroll" in sections[i].lower()
            ) and "proof" not in sections[i].lower():
                if "corollary to" in sections[i].lower():
                    corollary_to = self.get_premises(sections[i])
                theorem_content = theorem_content + "\n\n" + sections_content[i]

            elif "proof" in sections[i].lower():
                if "{{:" not in sections_content[i] and sections_content[i].strip():

                    proofs.append(self.replace_refs(sections_content[i]))
                    premises = self.get_premises(sections_content[i])
                    all_premises.extend(premises)
            theorem_content_def = self.get_definitions(theorem_content)
            theorem_content = self.replace_refs(theorem_content)
        if (
            len(proofs) > 0
            and len(theorem_content.strip()) > 0
            and "{{:" not in theorem_content
            and corollary_to
        ):
            return [theorem_content, proofs, all_premises, corollary_to]
        else:
            return []
