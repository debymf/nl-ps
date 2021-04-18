from prefect import Task
from dynaconf import settings
from loguru import logger
from tqdm import tqdm
import json

OUTPUT_FOLDER = "./output/"


class GenerateOutputTask(Task):
    def run(self, definitions, lemmas, corollaries, theorems):
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

        # for title, content in out_theorems.items():
        #     title_file = title.replace("/", "_")
        #     with open(f"./output/theorems/{title_file}.json", "w") as f:
        #         entry = {
        #             title: {
        #                 "content": content["content"],
        #                 "category": content["category"],
        #                 "premises": content["premises"],
        #             }
        #         }
        #         json.dump(entry, f)

        # for title, content in out_lemmas.items():
        #     title_file = title.replace("/", "_")
        #     with open(f"./output/lemmas/{title_file}.json", "w") as f:
        #         entry = {
        #             title: {
        #                 "content": content["content"],
        #                 "category": content["category"],
        #                 "premises": content["premises"],
        #             }
        #         }
        #         json.dump(entry, f)

        # for title, content in out_corollaries.items():
        #     title_file = title.replace("/", "_")
        #     with open(f"./output/corollaries/{title_file}.json", "w") as f:
        #         entry = {
        #             title: {
        #                 "content": content["content"],
        #                 "category": content["category"],
        #                 "premises": content["premises"],
        #             }
        #         }
        #         json.dump(entry, f)

        # for title, content in out_definitions.items():
        #     title_file = title.replace("/", "_")
        #     with open(f"./output/definitions/{title_file}.json", "w") as f:
        #         entry = {
        #             title: {
        #                 "content": content["content"],
        #                 "category": content["category"],
        #             }
        #         }
        #         json.dump(entry, f)

        with open(f"./output/theorems.json", "w") as f:
            json.dump(out_theorems, f)
        with open(f"./output/lemmas.json", "w") as f:
            json.dump(out_lemmas, f)
        with open(f"./output/corollaries.json", "w") as f:
            json.dump(out_corollaries, f)
        with open(f"./output/definitions.json", "w") as f:
            json.dump(out_definitions, f)
