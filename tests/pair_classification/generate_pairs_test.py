import unittest
from loguru import logger
from nlps_extraction.tasks.pair_classification import GeneratePairsTask


class GeneratePairsTest(unittest.TestCase):
    def test_generate_pairs(self):
        gen_task = GeneratePairsTask()
        gen_task.run()
