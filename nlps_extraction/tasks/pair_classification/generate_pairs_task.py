from prefect import Task
from loguru import logger
import json
from tqdm import tqdm
import numpy as np
from nlps_extraction.util.bm25 import BM25Fit, BM25Search
import os

INPUT_FOLDER = "./dataset/"
OUTPUT_FOLDER = "./dataset/"


class GeneratePairsTask(Task):
    def build_pairs(
        self,
        premises_dict,
        encoder,
        encoder_statement,
        kb,
        num_neg=1,
        hard_negative=False,
    ):
        if hard_negative:
            logger.info("HARD EXAMPLES")
            fit_class = BM25Fit()
            all_st = dict()
            for title, p in premises_dict.items():
                all_st[title] = encoder_statement[encoder[title]]
                for x in p:
                    all_st[x] = encoder_statement[encoder[x]]
            for title in kb:
                all_st[title] = encoder_statement[encoder[title]]

            ix = fit_class.run(all_st)
            search_class = BM25Search()
            retrieval_results = search_class.run(all_st, ix)

            all_pairs = dict()
            i = 0
            for title, premises in tqdm(premises_dict.items()):
                if title in encoder:
                    for p in premises:
                        if p in encoder:
                            all_pairs[i] = {
                                "statement_1": encoder[title],
                                "statement_2": encoder[p],
                                "score": 1,
                            }
                            i = i + 1
                            closest = list(retrieval_results[p].keys())[1:]

                            total_negatives = num_neg
                            for _ in range(total_negatives):
                                not_in = 1

                                while not_in == 1:
                                    if len(closest) == 0:
                                        closest = list(retrieval_results[p].keys())[1:]
                                    negative_example = closest[0]
                                    closest = closest[1:]
                                    if (
                                        negative_example != title
                                        and negative_example not in premises
                                    ):
                                        not_in = 0

                                    all_pairs[i] = {
                                        "statement_1": encoder[title],
                                        "statement_2": encoder[negative_example],
                                        "score": 0,
                                    }
                                    i = i + 1

        else:
            logger.info("RANDOM EXAMPLES")
            all_pairs = dict()
            i = 0
            for title, premises in tqdm(premises_dict.items()):
                if title in encoder:
                    for p in premises:
                        if p in encoder:
                            all_pairs[i] = {
                                "statement_1": encoder[title],
                                "statement_2": encoder[p],
                                "score": 1,
                            }
                            i = i + 1
                    total_negatives = len(premises) * num_neg
                    negative_examples = np.random.choice(kb, total_negatives)
                    for n in negative_examples:
                        if n in encoder:
                            all_pairs[i] = {
                                "statement_1": encoder[title],
                                "statement_2": encoder[n],
                                "score": 0,
                            }
                            i = i + 1

        return all_pairs

    def run(self, hard_negative=False):
        if hard_negative:
            file_type_string = "similar"
        else:
            file_type_string = "random"

        with open(INPUT_FOLDER + "train.json", "r") as f:
            train = json.load(f)
        with open(INPUT_FOLDER + "test.json", "r") as f:
            test = json.load(f)
        with open(INPUT_FOLDER + "dev.json", "r") as f:
            dev = json.load(f)
        with open(INPUT_FOLDER + "statements.json", "r") as f:
            statements = json.load(f)
        with open(INPUT_FOLDER + "kb.json", "r") as f:
            kb = json.load(f)

        logger.info(f"Train: {len(train)}")
        logger.info(f"Test: {len(test)}")
        logger.info(f"Dev: {len(dev)}")

        encoder_title = dict()
        decoder_title = dict()
        encoder_statements = dict()
        decoder_statements = dict()
        for title, content in statements.items():
            encoder_title[title] = len(encoder_title)
            decoder_title[encoder_title[title]] = title
            encoder_statements[encoder_title[title]] = content

        logger.info("Building train")
        train_pairs_1 = self.build_pairs(
            train, encoder_title, encoder_statements, kb, num_neg=1
        )
        logger.info(f"Train pairs: {len(train_pairs_1)} -- NUM_NEGATIVES = 1")
        train_pairs_2 = self.build_pairs(
            train, encoder_title, encoder_statements, kb, num_neg=2
        )
        logger.info(f"Train pairs: {len(train_pairs_2)} -- NUM_NEGATIVES = 2")
        train_pairs_5 = self.build_pairs(
            train, encoder_title, encoder_statements, kb, num_neg=5
        )
        logger.info(f"Train pairs: {len(train_pairs_5)} -- NUM_NEGATIVES = 5")
        train_pairs_10 = self.build_pairs(
            train, encoder_title, encoder_statements, kb, num_neg=10
        )
        logger.info(f"Train pairs: {len(train_pairs_10)} -- NUM_NEGATIVES = 10")

        logger.info("Building test")
        test_pairs_1 = self.build_pairs(
            test, encoder_title, encoder_statements, kb, num_neg=1
        )
        logger.info(f"Test pairs: {len(test_pairs_1)} -- NUM_NEGATIVES = 1")
        test_pairs_2 = self.build_pairs(
            test, encoder_title, encoder_statements, kb, num_neg=2
        )
        logger.info(f"Test pairs: {len(test_pairs_2)} -- NUM_NEGATIVES = 2")
        test_pairs_5 = self.build_pairs(
            test, encoder_title, encoder_statements, kb, num_neg=5
        )
        logger.info(f"Test pairs: {len(test_pairs_5)} -- NUM_NEGATIVES = 5")
        test_pairs_10 = self.build_pairs(
            test, encoder_title, encoder_statements, kb, num_neg=10
        )
        logger.info(f"Test pairs: {len(test_pairs_10)} -- NUM_NEGATIVES = 10")

        logger.info("Building dev")
        dev_pairs_1 = self.build_pairs(
            dev, encoder_title, encoder_statements, kb, num_neg=1
        )
        logger.info(f"dev pairs: {len(dev_pairs_1)} -- NUM_NEGATIVES = 1")
        dev_pairs_2 = self.build_pairs(
            dev, encoder_title, encoder_statements, kb, num_neg=2
        )
        logger.info(f"dev pairs: {len(dev_pairs_2)} -- NUM_NEGATIVES = 2")
        dev_pairs_5 = self.build_pairs(
            dev, encoder_title, encoder_statements, kb, num_neg=5
        )
        logger.info(f"dev pairs: {len(dev_pairs_5)} -- NUM_NEGATIVES = 5")
        dev_pairs_10 = self.build_pairs(
            dev, encoder_title, encoder_statements, kb, num_neg=10
        )
        logger.info(f"dev pairs: {len(dev_pairs_10)} -- NUM_NEGATIVES = 10")

        if not os.path.exists(OUTPUT_FOLDER + file_type_string + "_pairs/"):
            os.makedirs(OUTPUT_FOLDER + file_type_string + "_pairs/")

        with open(
            OUTPUT_FOLDER + file_type_string + "_pairs/statements_encoding.json", "w"
        ) as f:
            json.dump(encoder_statements, f)

        with open(
            OUTPUT_FOLDER + file_type_string + "_pairs/titles_decoding.json", "w"
        ) as f:
            json.dump(decoder_title, f)

        with open(
            OUTPUT_FOLDER + file_type_string + "_pairs/train_pairs1.json", "w"
        ) as f:
            json.dump(train_pairs_1, f)
        with open(
            OUTPUT_FOLDER + file_type_string + "_pairs/train_pairs2.json", "w"
        ) as f:
            json.dump(train_pairs_2, f)
        with open(
            OUTPUT_FOLDER + file_type_string + "_pairs/train_pairs5.json", "w"
        ) as f:
            json.dump(train_pairs_5, f)
        with open(
            OUTPUT_FOLDER + file_type_string + "_pairs/train_pairs10.json", "w"
        ) as f:
            json.dump(train_pairs_10, f)

        with open(
            OUTPUT_FOLDER + file_type_string + "_pairs/test_pairs1.json", "w"
        ) as f:
            json.dump(test_pairs_1, f)
        with open(
            OUTPUT_FOLDER + file_type_string + "_pairs/test_pairs2.json", "w"
        ) as f:
            json.dump(test_pairs_2, f)
        with open(
            OUTPUT_FOLDER + file_type_string + "_pairs/test_pairs5.json", "w"
        ) as f:
            json.dump(test_pairs_5, f)
        with open(
            OUTPUT_FOLDER + file_type_string + "_pairs/test_pairs10.json", "w"
        ) as f:
            json.dump(test_pairs_10, f)

        with open(
            OUTPUT_FOLDER + file_type_string + "_pairs/dev_pairs1.json", "w"
        ) as f:
            json.dump(dev_pairs_1, f)
        with open(
            OUTPUT_FOLDER + file_type_string + "_pairs/dev_pairs2.json", "w"
        ) as f:
            json.dump(dev_pairs_2, f)
        with open(
            OUTPUT_FOLDER + file_type_string + "_pairs/dev_pairs5.json", "w"
        ) as f:
            json.dump(dev_pairs_5, f)
        with open(
            OUTPUT_FOLDER + file_type_string + "_pairs/dev_pairs10.json", "w"
        ) as f:
            json.dump(dev_pairs_10, f)
