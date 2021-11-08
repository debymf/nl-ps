from prefect import Task
from loguru import logger
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm
import ml_metrics as metrics
from nlps_extraction.util import compute_mean_average_precision
import torch


class EvaluateSBertTask(Task):
    def get_closest(
        self, conjecture_embedding, statements_embedding, score_function=util.cos_sim
    ):
        retrieved = util.semantic_search(
            conjecture_embedding,
            list(statements_embedding.values()),
            score_function=score_function,
            top_k=30000,
        )

        all_titles = list(statements_embedding.keys())

        retrieved_list = list()
        for element in retrieved[0]:
            retrieved_list.append(all_titles[element["corpus_id"]])

        return retrieved_list

    def get_map(self, statements, kb, model, score_function):

        all_retrieved = list()
        all_premises = list()
        for title, content in tqdm(statements.items()):
            conjecture_embedding = model.encode(
            content["text"],  convert_to_tensor=True)
            retrieved = self.get_closest(conjecture_embedding, kb, score_function)
            premises = [str(p) for p in content["premises"]]
            
            all_retrieved.append(retrieved)
            all_premises.append(premises)
            
        map_value = compute_mean_average_precision(all_premises, all_retrieved)


        logger.info(f"Map_value = {map_value}")


    def run(self, input_data, encoded_kb, model_name, score_function=util.cos_sim):
        model = SentenceTransformer(model_name)

        logger.info("Getting Test results")
        self.get_map(input_data["test"], encoded_kb, model,score_function)

        logger.info("Getting Dev results")
        self.get_map(input_data["dev"], encoded_kb, model,score_function)


