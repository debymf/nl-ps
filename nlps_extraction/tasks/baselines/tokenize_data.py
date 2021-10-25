from prefect import Task
from dynaconf import settings
from loguru import logger
from tqdm import tqdm
import json
from nlps_extraction.util import (
    tokenize_exp_as_words_dict,
    tokenize_exp_as_symbols_dict,
)


class CustomTokenizeInput(Task):
    def run(self, input_data, expression_as_words=False):
        tokenized_input = dict()

        tokenized_input["kb"] = dict()
        if expression_as_words:
            tokenized_input["kb"] = tokenize_exp_as_words_dict(input_data["kb"])
        else:
            tokenized_input["kb"] = tokenize_exp_as_symbols_dict(input_data["kb"])

        for data_split in ["train", "test", "dev"]:
            tokenized_input[data_split] = input_data[data_split]
            for title_key, _ in tokenized_input[data_split].items():
                tokenized_input[data_split][title_key]["text"] = tokenized_input["kb"][
                    title_key
                ]

        return tokenized_input
