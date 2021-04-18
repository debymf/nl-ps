from prefect import Task
from dynaconf import settings
from loguru import logger
from tqdm import tqdm
import regex as re
import os.path
import sys


class FixRedirectsTask(Task):
    def run(self, entries):

        entries, redirects = self.find_and_remove_redirect(entries)

        redirects = self.solve_dependencies_redirects(redirects)

        entries = self.replace_redirects(entries, redirects)

        logger.info(f"Total statements after fix: {len(entries)}")

        return entries

    def find_and_remove_redirect(self, entries):
        """
        Function used to find and remove redirects from the text.

        :param entries: entries to be checked

        :return: List of clean entries, and the redirect link.
        """
        redirect = []
        titles_list = [title for title, content in entries.items()]
        new_redirects = dict()
        logger.info("** Finding redirects **")
        for title, text in tqdm(entries.items()):
            if "#redirect" in text.lower():
                redirect_link = re.findall(
                    "\#[r|R][e|E][d|D][i|I][R|r][E|e][C|c][T|t]:* *\[*(.*)?\]\]", text
                )
                redirect_title = redirect_link[0]
                if "#" in redirect_title:
                    redirect_title = redirect_title.split("#")[0]
                if "|" in redirect_title:
                    redirect_title = redirect_title.split("|")[0]
                if redirect_title not in titles_list:
                    redirect_title = self.treat_specific_cases_redirect(title)

                redirect.append((title, redirect_title))
            else:
                new_redirects[title] = text
        logger.info(f"Number of redirects found: {len(redirect)}")

        return new_redirects, redirect

    def solve_dependencies_redirects(self, redirects: list) -> list:
        """
        Find redirects that take to other redirects

        :param redirects: list of redirects

        :return: List of clean redirects
        """

        logger.info("*** Solving dependecies between redirects ***")
        for start, end in tqdm(redirects):
            for i in range(0, len(redirects)):
                if redirects[i][1] == start:
                    redirects[i] = (redirects[i][0], end)

        return redirects

    def replace_redirects(self, entries, redirects: list):
        """
        Function that takes redirects and replaces it in the proof.

        :param entries: proofwiki entries.
        :param redirects: list of connected redirects.

        :return: entries without redirects.
        """
        logger.info("*** Replacing redirects (This might take some time...) ***")
        new_entries = dict()
        for start, end in tqdm(redirects):
            for title, content in entries.items():
                if start in content:
                    new_entries[title] = content.replace(start, end)
        return entries

    def treat_specific_cases_redirect(self, title):
        """
        Function used to treat special cases of redirects.

        :param title: special case title

        :return: a pair of the current title and the redirect.
        """

        replacements = {
            "Definition:Exponential/Definition 5": "Definition:Exponential Function",
            "Definition:polynomial over Ring in One Variable": "Definition:Polynomial over Ring/One Variable",
            "Definition:Double Root (Polynomial)": "Definition:Multiplicity (Polynomial)",
            "Definition:Polyhedron Inscribed in Sphere": "Definition:Inscribe",
            "Definition:Non-Negative Real Number": "Definition:Positive/Real Number",
        }

        return replacements.get(title, title)
