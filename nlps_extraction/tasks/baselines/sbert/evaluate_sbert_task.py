from prefect import Task
from loguru import logger
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm
import ml_metrics as metrics
import torch


class EvaluateSBertTask(Task):
    def get_closest(
        self, conjecture_embedding, statements_embedding, score_function=util.cos_sim
    ):

        retrieved = util.semantic_search(
            torch.Tensor(conjecture_embedding),
            list(statements_embedding.values()),
            score_function=score_function,
            top_k=5,
        )

        print(retrieved)
        input()

        all_titles = list(statements_embedding.keys())

        return retrieved

    def get_map(self, statements, kb, score_function):

        for title, content in tqdm(statements.items()):
            retrieved = self.get_closest(kb[title], kb, score_function)[0]
            # retrieved_index = [result["corpus_id"] for result in retrieved]
            # premises = content["premises"]

            # map_value = metrics.mapk(retrieved_index, premises, len(kb))
            # print(map_value)
            # input()

    def run(self, input_data, encoded_kb, score_function=util.cos_sim):
        logger.info("Getting Test results")
        self.get_map(input_data["test"], encoded_kb, score_function)

        # logger.info("Getting Dev results")
        # self.get_map(input_data["dev"], encoded_kb, score_function)

