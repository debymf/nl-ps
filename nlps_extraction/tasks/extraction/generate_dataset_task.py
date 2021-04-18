from prefect import Task
from dynaconf import settings
from loguru import logger
from tqdm import tqdm
import json
from sklearn.model_selection import train_test_split
import sys


OUTPUT_FOLDER = "./dataset/"
# SELECTED_CATEGORY = "Set Theory"


class GenerateDatasetTask(Task):
    def run(self):
        with open("./output/lemmas.json", "r") as f:
            lemmas = json.load(f)

        with open("./output/corollaries.json", "r") as f:
            corollaries = json.load(f)

        with open("./output/theorems.json", "r") as f:
            theorems = json.load(f)

        with open("./output/definitions.json", "r") as f:
            definitions = json.load(f)

        all_statements = dict()

        for title, content in lemmas.items():
            clean_content = content["content"].strip()

            # if clean_content and content["category"] == SELECTED_CATEGORY:
            all_statements[title] = clean_content

        for title, content in theorems.items():
            clean_content = content["content"].strip()

            # if clean_content and content["category"] == SELECTED_CATEGORY:
            #     all_statements[title] = clean_content

        for title, content in corollaries.items():
            clean_content = content["content"].strip()

            # if clean_content and content["category"] == SELECTED_CATEGORY:
            all_statements[title] = clean_content

        for title, content in definitions.items():
            clean_content = content["content"].strip()

            # if clean_content and content["category"] == SELECTED_CATEGORY:
            all_statements[title] = clean_content
        logger.info(f"All statements: {len(all_statements)}")

        has_premises = dict()
        all_definitions = definitions

        new_defintions = dict()
        for title, content in all_definitions.items():
            # if content["category"] == SELECTED_CATEGORY:
            new_defintions[title] = content

        all_definitions = dict(new_defintions)

        for title, content in lemmas.items():
            if title in all_statements:
                premises = [
                    p for p in content["premises"] if p in all_statements and p != title
                ]
                if premises:
                    has_premises[title] = premises

        for title, content in theorems.items():
            if title in all_statements:
                premises = [
                    p for p in content["premises"] if p in all_statements and p != title
                ]
                if premises:
                    has_premises[title] = premises

        for title, content in corollaries.items():
            if title in all_statements:
                premises = [
                    p for p in content["premises"] if p in all_statements and p != title
                ]
                if premises:
                    has_premises[title] = premises

        logger.info(f"Has premises: {len(has_premises)}")

        is_premise_of = dict()
        for title, premises in has_premises.items():
            for p in premises:
                if p not in is_premise_of:
                    is_premise_of[p] = list()
                is_premise_of[p].append(title)

        equal_content = dict()
        dict_content = dict()
        for title_a, content_a in tqdm(all_statements.items()):
            if content_a in dict_content:
                equal_content[title_a] = dict_content[content_a]
            else:
                dict_content[content_a] = title_a

        logger.info("Fixing premises")
        logger.info(f"Before fix: {len(has_premises)}")

        for title_a, title_b in tqdm(equal_content.items()):
            if title_a in has_premises:
                premises = has_premises[title_a]
                del has_premises[title_a]
                if title_b in has_premises:
                    has_premises[title_b].extend(premises)
                else:
                    has_premises[title_b] = premises
            if title_a in is_premise_of:
                for element in is_premise_of[title_a]:
                    if element in has_premises:
                        has_premises[element] = [
                            title_b if premise == title_a else premise
                            for premise in has_premises[element]
                        ]

        logger.info("Fixing premises")
        logger.info(f"After fix: {len(has_premises)}")

        has_premises_titles = list(has_premises.keys())
        (
            has_premises_train,
            has_premises_test,
        ) = train_test_split(has_premises_titles, test_size=0.40, random_state=42)

        (
            has_premises_test,
            has_premises_dev,
        ) = train_test_split(has_premises_test, test_size=0.50, random_state=42)

        kb = list()
        train = dict()
        all_entries = list()
        train_premises = list()
        for title in has_premises_train:
            premise_list = list()
            for p in has_premises[title]:
                if p not in has_premises_test and p not in has_premises_dev:
                    premise_list.append(p)

            if premise_list:
                train[title] = premise_list
                all_entries.append(title)
                all_entries.extend(premise_list)
                train_premises.extend(premise_list)

        dev = dict()
        for title in has_premises_dev:
            premise_list = list()
            for p in has_premises[title]:
                if (
                    p in has_premises_train
                    or p in all_definitions
                    or p in train_premises
                ):
                    premise_list.append(p)

            if premise_list:
                dev[title] = premise_list
                all_entries.append(title)
                all_entries.extend(premise_list)

        test = dict()
        for title in has_premises_test:
            premise_list = list()
            for p in has_premises[title]:
                if (
                    p in has_premises_train
                    or p in all_definitions
                    or p in train_premises
                ):
                    premise_list.append(p)

            if premise_list:
                test[title] = premise_list
                all_entries.append(title)
                all_entries.extend(premise_list)

        new_statements = dict()
        for title, content in all_statements.items():
            if title in all_entries:
                new_statements[title] = content

        kb = list()
        for title, premises in train.items():
            kb.append(title)
            kb.extend(premises)

        logger.info(f"Train {len(train)}")

        logger.info(f"Dev {len(dev)}")
        logger.info(f"Test {len(test)}")
        with open(OUTPUT_FOLDER + "train.json", "w") as f:
            json.dump(train, f)
        with open(OUTPUT_FOLDER + "test.json", "w") as f:
            json.dump(test, f)
        with open(OUTPUT_FOLDER + "dev.json", "w") as f:
            json.dump(dev, f)
        with open(OUTPUT_FOLDER + "statements.json", "w") as f:
            json.dump(new_statements, f)
        with open(OUTPUT_FOLDER + "kb.json", "w") as f:
            json.dump(kb, f)

        # with open(OUTPUT_FOLDER + "lemmas.json", "w") as f:
        #     json.dump(out_lemmas, f)

        # with open(OUTPUT_FOLDER + "theorems.json", "w") as f:
        #     json.dump(out_theorems, f)

        # with open(OUTPUT_FOLDER + "corollaries.json", "w") as f:
        #     json.dump(out_corollaries, f)
