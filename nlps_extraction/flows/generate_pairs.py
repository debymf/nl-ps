from prefect import Flow, task
from prefect.engine.flow_runner import FlowRunner
from nlps_extraction.tasks.extraction import GenerateDatasetTask
from nlps_extraction.tasks.pair_classification import GeneratePairsTask


gen_data_task = GenerateDatasetTask()
gen_pairs_task = GeneratePairsTask()

with Flow("Generate data for tasks") as flow:
    xml_file = gen_data_task()
    gen_pairs_task(hard_negative=False)
    gen_pairs_task(hard_negative=True)


FlowRunner(flow=flow).run()
