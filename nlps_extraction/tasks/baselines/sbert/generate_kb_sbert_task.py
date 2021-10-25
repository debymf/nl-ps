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

        titles_embedding = list(input_data.keys())
        embedding_kb_output = model.encode(
            list(input_data.values()), show_progress_bar=True
        )

        for title, embedding in zip(titles_embedding, embedding_kb_output):
            print(type(title))
            print(embedding)
            input()
            embedding_kb[title] = embedding

        return embedding_kb

