from prefect import Task
from dynaconf import settings
from loguru import logger
from tqdm import tqdm
import regex as re
import sys


class RawContent:
    def __init__(self, onlyinclude, title, content):
        self.onlyinclude = onlyinclude
        self.title = title
        self.content = content


class FixSnippetsTask(Task):
    def run(self, entries):
        logger.info("Starting Fixing Snippets")
        logger.info("Building raw content for each entry")
        raw_entries_dict = self.build_raw_content(entries)
        logger.info("Processing Only Include tags ")
        entries_dict = self.process_only_include(entries, raw_entries_dict)

        return entries_dict

    def build_raw_content(self, entries):
        raw_content_dict = dict()
        for title, text in entries.items():
            if "<onlyinclude>" in text and "</onlyinclude>" in text:
                include_text = self.find_only_include(text)
            else:
                include_text = text
            r = RawContent(include_text, title, text)
            raw_content_dict[title] = r

        return raw_content_dict

    def find_only_include(self, text):
        to_find = r"<onlyinclude>(.*)</onlyinclude>"
        matches = re.findall(to_find, text, re.MULTILINE | re.DOTALL)
        return matches[0]

    def process_only_include(self, entries, raw_content):
        new_entries = dict()
        pattern = r"{{:(.*?)}}"
        for title, content in tqdm(entries.items()):
            matches = re.findall(pattern, content, flags=0)

            for m in matches:
                if m in raw_content:
                    content = content.replace(
                        "{{:" + m + "}}", raw_content[m].onlyinclude
                    )
                else:
                    content = content.replace("{{:" + m + "}}", "")
            new_entries[title] = content.replace("<onlyinclude>", "").replace(
                "</onlyinclude>", ""
            )

        return new_entries
