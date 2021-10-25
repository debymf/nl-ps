from prefect import Task
from dynaconf import settings
from loguru import logger
from tqdm import tqdm
import json
from nlps_extraction.util import BM25Fit, BM25Search


class GenerateKBTFIDFTask(Task):
    def run(self, kb):
        fit_class = BM25Fit()
        ix = fit_class.run(kb)

        return ix

