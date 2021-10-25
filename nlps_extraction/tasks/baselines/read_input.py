from prefect import Task
from dynaconf import settings
from loguru import logger
from tqdm import tqdm
import json


class ReadPSInput(Task):
    def run(self):

        with open(f"./output/test.json", "r") as f:
            test = json.load(f)

        with open(f"./output/dev.json", "r") as f:
            dev = json.load(f)

        with open(f"./output/train.json", "r") as f:
            train = json.load(f)

        with open(f"./output/kb.json", "r") as f:
            kb = json.load(f)

        logger.info(f"Train size: {len(train)}")
        logger.info(f"Dev size: {len(dev)}")
        logger.info(f"Test size: {len(test)}")
        logger.info(f"KB size: {len(kb)}")
        return {"kb": kb, "train": train, "test": test, "dev": dev}
