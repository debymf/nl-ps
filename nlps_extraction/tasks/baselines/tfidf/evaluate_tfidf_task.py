from prefect import Task
from dynaconf import settings
from loguru import logger
from tqdm import tqdm
import json
from nlps_extraction.util import BM25Fit, BM25Search, compute_mean_average_precision




class EvaluateTFIDFTask(Task):
    def get_retrieved_premises(self, statements, ix, kb):
        search_class = BM25Search()
        text_only = {
            key_title: statements[key_title]["text"]
            for key_title, _ in statements.items()
        }

        retrieval_results = search_class.run(text_only, ix)


        retrieval_results_list = list()
        actual_results_list = list()
        for title, content in statements.items():
            retrieval_results_list.append(list(retrieval_results[title].keys()))
            actual_results_list.append([str(p) for p in content["premises"]])

            
            premises = content["premises"]
            

        map_value = compute_mean_average_precision(actual_results_list, retrieval_results_list)

        logger.info(f"mAP: {map_value}")

    def run(self, input_data, ix):
        search_class = BM25Search()

        logger.info("Test set:")
        self.get_retrieved_premises(input_data["test"], ix, input_data["kb"])

        logger.info("Dev set:")
        self.get_retrieved_premises(input_data["dev"], ix, input_data["kb"])

        return ix

