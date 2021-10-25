from prefect import Task
from loguru import logger
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm


class GenerateKBSBertTask(Task):
    def run(self, input_data, model_name):
        logger.info("** Converting Sentences to Vector **")
        model = SentenceTransformer(model_name)

        logger.info("** Embedding KB **")
        embedding_kb = dict()

        titles_embedding = list(input_data.keys())
        embedding_kb_output = model.encode(
            list(input_data.values()), show_progress_bar=True, convert_to_tensor=True
        )

        for title, embedding in zip(titles_embedding, embedding_kb_output):
            embedding_kb[str(title)] = embedding

        return embedding_kb

