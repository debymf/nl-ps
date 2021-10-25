from prefect import Task
from loguru import logger
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm


class GenerateKBSBertTask(Task):
    def run(self, input_data, model):
        logger.info("** Converting Sentences to Vector **")
        model = SentenceTransformer(model)

        logger.info("** Embedding KB **")
        embedding_kb = dict()

        embedding_kb_output = model.encode(
            list(input_data.values()), show_progress_bar=True
        )

        print(type(embedding_kb_output))
        input()

        return embedding_kb

