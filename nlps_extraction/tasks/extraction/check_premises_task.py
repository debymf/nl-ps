from prefect import Task
from dynaconf import settings
from loguru import logger
from tqdm import tqdm
import networkx as nx


class CheckPremisesTask(Task):
    def run(self, definitions, lemmas, corollaries, theorems):
        all_titles = list()
        G = nx.DiGraph()
        logger.info("Limiting the number of premises...")
        for title, element in definitions.items():
            all_titles.append(title)

        for title, element in lemmas.items():
            all_titles.append(title)

        for title, element in corollaries.items():
            all_titles.append(title)

        for title, element in theorems.items():
            all_titles.append(title)

        logger.info("Total entries")
        logger.info(len(all_titles))

        premises_dict = dict()

        new_theorems = dict()
        for title, element in tqdm(theorems.items(), desc="Checking Theorem premises"):
            category = element[0]
            text = element[1]
            proofs = element[2]
            all_premises = element[3]
            new_all_premises = list()

            for premises in all_premises:
                new_premises = list()
                for p in premises:
                    if p in all_titles and p != title:
                        if self.check_for_no_cycles(G, title, p):
                            new_premises.append(p)
                            G.add_edge(title, p)
                new_all_premises.append(new_premises)
                if not new_all_premises:
                    print(title)
            new_theorems[title] = [category, text, proofs, new_all_premises]

        new_lemmas = dict()
        for title, element in tqdm(lemmas.items(), desc="Checking Lemma premises"):
            category = element[0]
            text = element[1]
            proofs = element[2]
            all_premises = element[3]
            new_all_premises = list()

            for premises in all_premises:
                new_premises = list()
                for p in premises:
                    if p in all_titles and p != title:
                        if self.check_for_no_cycles(G, title, p):
                            new_premises.append(p)
                            G.add_edge(title, p)

                new_all_premises.append(new_premises)
                if not new_all_premises:
                    print(title)
            premises_dict[title] = new_all_premises
            new_lemmas[title] = [category, text, proofs, new_all_premises]

        new_corollaries = dict()
        for title, element in tqdm(
            corollaries.items(), desc="Checking Corollary premises"
        ):
            category = element[0]
            text = element[1]
            proofs = element[2]
            all_premises = element[3]
            corollary_to = element[4]
            new_all_premises = list()

            for premises in all_premises:
                new_premises = list()
                for p in premises:
                    if p in all_titles and p != title:
                        if self.check_for_no_cycles(G, title, p):
                            new_premises.append(p)
                            G.add_edge(title, p)
                new_all_premises.append(new_premises)
                if not new_all_premises:
                    print(title)
            new_corollaries[title] = [
                category,
                text,
                proofs,
                new_all_premises,
                corollary_to,
            ]

        return {
            "theorems": new_theorems,
            "lemmas": new_lemmas,
            "corollaries": new_corollaries,
        }

    def check_for_no_cycles(self, graph, title, premise):
        graph.add_edge(title, premise)
        if len(list(nx.simple_cycles(graph))) > 0:
            return False
        else:
            return True
