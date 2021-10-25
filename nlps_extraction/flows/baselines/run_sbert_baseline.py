from prefect import Flow, task
from prefect.engine.flow_runner import FlowRunner
from nlps_extraction.tasks.baselines import ReadPSInput, CustomTokenizeInput
from nlps_extraction.tasks.baselines.sbert import GenerateKBSBertTask, EvaluateSBertTask
from prefect.engine.results import LocalResult

cache_args = dict(
    target="{task_name}.pkl", checkpoint=True, result=LocalResult(dir=f"./cache/"),
)


read_input_files = ReadPSInput()
tokenize_data = CustomTokenizeInput()
encode_kb_task = GenerateKBSBertTask()
evaluation_task = EvaluateSBertTask()

MODEL = "sentence-transformers/all-mpnet-base-v2"
with Flow("Running S-BERT baselines") as flow:
    input_files = read_input_files()
    encoded_kb = encode_kb_task(input_files["kb"], MODEL)
    evaluation_task(input_files, encoded_kb)


FlowRunner(flow=flow).run()
