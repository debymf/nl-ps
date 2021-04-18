from prefect import Task
from dynaconf import settings
from loguru import logger
from tqdm import tqdm


class ModelTask(Task):
    def run(self):
        print("test")
