from prefect import Flow, task
from prefect.engine.flow_runner import FlowRunner
from nlps_extraction.tasks.baselines import ReadPSInput, CustomTokenizeInput
from nlps_extraction.tasks.baselines.tfidf import GenerateKBTFIDFTask, EvaluateTFIDFTask
from prefect.engine.results import LocalResult

cache_args = dict(
    target="{task_name}.pkl", checkpoint=True, result=LocalResult(dir=f"./cache/"),
)


read_input_files = ReadPSInput(**cache_args)
tokenize_data = CustomTokenizeInput(**cache_args)
encode_kb_task = GenerateKBTFIDFTask(**cache_args)
evaluation_task = EvaluateTFIDFTask()


with Flow("Running TF-IDF baselines") as flow:
    input_files = read_input_files()
    tokenized_input = tokenize_data(input_files)
    encoded_kb = encode_kb_task(tokenized_input["kb"])
    evaluation_task(tokenized_input, encoded_kb)


FlowRunner(flow=flow).run()
