from prefect import Task
from dynaconf import settings
from loguru import logger
from tqdm import tqdm
import json
import uuid
import regex
import pandas as pd
from sklearn.model_selection import train_test_split

OUTPUT_FOLDER = "./output/"


class GenerateOutputTask(Task):
    def create_kb(self, definitions, lemmas, corollaries, theorems):
        def add_elements_to_kb(statements, kb, title_to_id, content_kb_list, type):
            content_kb_list = dict()
            for title, content in statements.items():
                new_id = str(uuid.uuid4())
                if content["content"] in content_kb_list:
                    matching_title = content_kb_list[content["content"]]
                    title_to_id[title] = title_to_id[matching_title]
                else:
                    content_kb_list[content["content"]] = title
                    kb[new_id] = dict()
                    kb[new_id]["text"] = content["content"].strip()
                    kb[new_id]["text"] = regex.sub("\\n+", "\\n", kb[new_id]["text"])
                    kb[new_id]["type"] =  type
                    kb[new_id]["category"] = content["category"]
                    title_to_id[title] = new_id

            return kb, title_to_id, content_kb_list

        def prepare_conjectures(statements, conjectures, content_to_id, title_to_id, type="none"):
            for title, content in statements.items():
                if content["content"] in content_to_id:
                    matching_title = content_to_id[content["content"]]
                    id_match = title_to_id[matching_title]
                    premises = content["premises"]
                    filtered_premises = list()
                    for p in premises:
                        if p in title_to_id:
                            filtered_premises.append(title_to_id[p])
                    if id_match in conjectures:
                        conjectures[id_match]["premises"].extend(filtered_premises)
                else:
                    content_to_id[content["content"]] = title
                    premises = content["premises"]
                    filtered_premises = list()
                    for p in premises:
                        if p in title_to_id:
                            filtered_premises.append(title_to_id[p])

                    
                    if filtered_premises:
                        new_id = title_to_id[title]
                        conjectures[new_id] = dict()
                        conjectures[new_id]["text"] = content["content"].strip()
                        conjectures[new_id]["text"] = regex.sub(
                            "\\n+", "\\n", conjectures[new_id]["text"]
                        )

                        conjectures[new_id]["premises"] = filtered_premises
                        conjectures[new_id]["category"] = content["category"]
                        conjectures[new_id]["type"] = type
            
            return conjectures, content_to_id

        title_to_id = dict()
        kb = dict()
        content_kb_list = list()
        kb, title_to_idd, content_kb_list = add_elements_to_kb(
            definitions, kb, title_to_id, content_kb_list, type="definitions"
        )

        kb, title_to_id, content_kb_list = add_elements_to_kb(
            lemmas, kb, title_to_id, content_kb_list, type="lemmas"
        )

        kb, title_to_id, content_kb_list = add_elements_to_kb(
            corollaries, kb, title_to_id, content_kb_list, type="corollaries"
        )

        kb, title_to_id, content_kb_list = add_elements_to_kb(
            theorems, kb, title_to_id, content_kb_list, type="theorem"
        )

        conjectures = dict()
        content_to_id = dict()
        conjectures, content_to_id = prepare_conjectures(
            theorems, conjectures, content_to_id, title_to_id, type="theorem"
        )
        conjectures, content_to_id = prepare_conjectures(
            lemmas, conjectures, content_to_id, title_to_id, type="lemma"
        )
        conjectures, content_to_id = prepare_conjectures(
            corollaries, conjectures, content_to_id, title_to_id, type="corollaries"
        )


        ## for  multi-hop settings 

        # for title_id, content in conjectures.items():
        #     premises = content["premises"]
        #     added_premises = list()
        #     for p in premises:
        #         if p in conjectures:
        #             added_premises.extend(conjectures[p]["premises"])
        #     premises.extend(added_premises)
        #     conjectures[title_id]["premises"] = list(set(premises))

        # for title_id, content in conjectures.items():
        #     premises = content["premises"]
            
        #     added_premises = list()
        #     for p in premises:
        #         if p in conjectures:
        #             added_premises.extend(conjectures[p]["premises"])
        #     premises.extend(added_premises)
        #     conjectures[title_id]["premises"] = list(set(premises))

        logger.info(f"Number of Conjecures: {len(conjectures)}")
        logger.info(f"KB size: {len(kb)}")

        return conjectures, kb

    def organise_input(self, definitions, lemmas, corollaries, theorems):
        out_definitions = dict()
        for title, content in definitions.items():
            out_definitions[title] = dict()
            out_definitions[title]["category"] = content[0]
            out_definitions[title]["content"] = content[1]
            out_definitions[title]["supporting_definitions"] = content[2]

        out_corollaries = dict()
        for title, content in corollaries.items():
            out_corollaries[title] = dict()
            out_corollaries[title]["category"] = content[0]
            out_corollaries[title]["content"] = content[1]
            out_corollaries[title]["proofs"] = content[2]
            out_corollaries[title]["premises"] = content[3]
            out_corollaries[title]["derived_from"] = content[4]

        out_lemmas = dict()
        for title, content in lemmas.items():
            out_lemmas[title] = dict()
            out_lemmas[title]["category"] = content[0]
            out_lemmas[title]["content"] = content[1]
            out_lemmas[title]["proofs"] = content[2]
            out_lemmas[title]["premises"] = content[3]

        out_theorems = dict()
        for title, content in theorems.items():
            out_theorems[title] = dict()
            out_theorems[title]["category"] = content[0]
            out_theorems[title]["content"] = content[1]
            out_theorems[title]["proofs"] = content[2]
            out_theorems[title]["premises"] = content[3]

        return out_definitions, out_lemmas, out_corollaries, out_theorems

    def split_data(self, data):

        s = pd.Series(data)
        training_data, test_data = [
            i.to_dict() for i in train_test_split(s, train_size=0.5, random_state=42)
        ]

        s = pd.Series(test_data)
        dev_data, test_data = [i.to_dict() for i in train_test_split(s, train_size=0.5, random_state=42)]

        logger.info(f"Training Data: {len(training_data)}")
        logger.info(f"Dev Data: {len(dev_data)}")
        logger.info(f"Test Data: {len(test_data)}")
        return training_data, dev_data, test_data

    def remove_eval_from_kb(self,kb, train, dev, test):
        def fix_split(split, kb):
            new_split = dict()
            for title_id, content in split.items():
                premises_list = list()
                for p in content["premises"]:
                    if p in kb:
                        premises_list.append(p)
                if premises_list:
                    new_split[title_id] = content
                    new_split[title_id]["premises"] = premises_list

            return new_split

        for id_title, _ in test.items():
            del kb[id_title]

        for id_title, _ in dev.items():
            del kb[id_title]

        new_test = fix_split(test, kb)
        new_train = fix_split(train, kb)
        new_dev = fix_split(dev, kb)

        return new_train, new_dev, new_test, kb
        
    def run(self, definitions, lemmas, corollaries, theorems):
        definitions, lemmas, corollaries, theorems = self.organise_input(
            definitions, lemmas, corollaries, theorems
        )

        logger.info(f"Number of definitions: {len(definitions)}")
        logger.info(f"Number of lemmas: {len(lemmas)}")
        logger.info(f"Number of corollaries: {len(corollaries)}")
        logger.info(f"Number of theoms: {len(theorems)}")

        conjectures, kb = self.create_kb(definitions, lemmas, corollaries, theorems)

        train, dev, test = self.split_data(conjectures)

        logger.info("DATA BEFORE CLEANING")
        logger.info(f"Training Data: {len(train)}")
        logger.info(f"Dev Data: {len(dev)}")
        logger.info(f"Test Data: {len(test)}")
        logger.info(f"KB Data: {len(kb)}")

        train, dev, test, kb = self.remove_eval_from_kb(kb, train, dev, test)

        logger.info("DATA AFTER CLEANING")
        logger.info(f"Training Data: {len(train)}")
        logger.info(f"Dev Data: {len(dev)}")
        logger.info(f"Test Data: {len(test)}")
        logger.info(f"KB Data: {len(kb)}")

        with open(f"./output/test.json", "w") as f:
            json.dump(test, f)

        with open(f"./output/dev.json", "w") as f:
            json.dump(dev, f)

        with open(f"./output/train.json", "w") as f:
            json.dump(train, f)

        # with open(f"./output/conjectures.json", "w") as f:
        #     json.dump(conjectures, f)
        with open(f"./output/kb.json", "w") as f:
            json.dump(kb, f)
        # with open(f"./output/corollaries.json", "w") as f:
        #     json.dump(out_corollaries, f)
        # with open(f"./output/definitions.json", "w") as f:
        #     json.dump(out_definitions, f)
