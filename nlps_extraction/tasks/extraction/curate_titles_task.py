from prefect import Task
from dynaconf import settings
from loguru import logger
from tqdm import tqdm
from nlps_extraction.util.caching import recover_cache, save_cache
import sys

CACHE_LOCATION = "./cache/curate_cache.msgpack"

TITLES_TO_REMOVE = [
    "User talk",
    "Mathematician",
    "User",
    "File",
    "Talk",
    "Book",
    "Definition talk",
    "Euclid",
    "Template",
    "Symbols",
    "Axiom",
    "Help",
    "Greek Anthology Book XIV",
    "Category talk",
    "Axiom talk",
    "ProofWiki",
    "Template talk",
    "MediaWiki",
    "Help talk",
    "Book talk",
    "Mathematician talk",
    "File talk",
    "ProofWiki talk",
    "Symbols talk",
]


class CurateTitlesTask(Task):
    def run(self, entries):
        logger.info("Running curation.")

        logger.info(f"Total before curation: {len(entries)}")
        selected_pages = dict()
        for title, content in entries.items():
            if title.split(":")[0] not in TITLES_TO_REMOVE:
                selected_pages[title] = content
        logger.info(f"Total after curation: {len(selected_pages)}")

        return selected_pages
