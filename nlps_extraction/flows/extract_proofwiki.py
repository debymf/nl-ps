from prefect import Flow, task
from prefect.engine.flow_runner import FlowRunner
from prefect.engine.results import LocalResult

from nlps_extraction.tasks.extraction import (
    FixRedirectsTask,
    XMLParserTask,
    FixSnippetsTask,
    GetCategoriesTask,
    CurateTitlesTask,
    GetDefinitionsTask,
    GetOthersTask,
    GenerateOutputTask,
)

cache_args = dict(
    target="{task_name}.pkl",
    checkpoint=True,
    result=LocalResult(dir=f"./cache/"),
)

parser_task = XMLParserTask(**cache_args)
fix_redirect_task = FixRedirectsTask(**cache_args)
fix_snippets_task = FixSnippetsTask(**cache_args)
get_categories_task = GetCategoriesTask(**cache_args)
curate_titles_task = CurateTitlesTask(**cache_args)
get_definitions_task = GetDefinitionsTask(**cache_args)
get_others_task = GetOthersTask(**cache_args)
generate_output_task = GenerateOutputTask(**cache_args)


with Flow("Run extraction flow") as flow:
    xml_file = parser_task()
    fixed_result = fix_redirect_task(xml_file)
    fixed_snippets = fix_snippets_task(fixed_result)
    out_categories = get_categories_task(fixed_snippets)
    curate_results = curate_titles_task(out_categories["out_entries"])
    out_definitions_task = get_definitions_task(
        curate_results, out_categories["definitions_category"]
    )
    get_others_out = get_others_task(
        out_definitions_task["others"], out_categories["others_categories"]
    )
    generate_output_task(
        out_definitions_task["definitions"],
        get_others_out["lemmas"],
        get_others_out["corollaries"],
        get_others_out["theorems"],
    )


FlowRunner(flow=flow).run()
