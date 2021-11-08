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

    def obtain_all_text(self, test, dev, kb):
        def get_all_text(split, all_text):
            for id_title, content in split.items():
                all_text[id_title] = content["text"]
            return all_text

        all_text = dict(kb)
        all_text = get_all_text(test, all_text)
        all_text = get_all_text(dev, all_text)

        return all_text
    
    def run(self, input_data, expression_as_words=True, char_level = False):
        tokenized_input = dict()

        all_text = self.obtain_all_text(input_data["test"], input_data["dev"], input_data["kb"])
        
    

        all_tokenized = dict()

        if expression_as_words:
            logger.info("Expressions are tokenized as words")
            all_tokenized = tokenize_exp_as_words_dict( all_text)
        else:
            if char_level:
                logger.info("Text is considered at char level")
                for title_index, content in  all_text.items():
                    all_tokenized[title_index] = list(content)
                
            else:
                logger.info("Expressions have its own tokeniser")
                all_tokenized = tokenize_exp_as_symbols_dict( all_text)


        tokenized_input["kb"] = dict(input_data["kb"])
        for title_key, _ in tokenized_input["kb"].items():
            tokenized_input["kb"][title_key] = all_tokenized[
                    title_key
                ]

        for data_split in ["train", "test", "dev"]:
            tokenized_input[data_split] = dict(input_data[data_split])
            for title_key, _ in tokenized_input[data_split].items():
                
                tokenized_input[data_split][title_key]["text"] = all_tokenized[
                    title_key
                ]

        return tokenized_input
