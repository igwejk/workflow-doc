#!/usr/bin/env python

from io import TextIOWrapper
from os import path
import pathlib
import yaml
import typer


def workflowdoc() -> None:
    """
    This is a utility for documenting a given GitHub Actions workflow by analysing
    the workflow file and generating a markdown documentation.
    """


app = typer.Typer(callback=workflowdoc, name="workflowdoc")


def read_workflow_description(workflow_file: TextIOWrapper) -> str:
    """
    Read the description of the workflow from the workflow file.
    """

    workflow_file.seek(0)
    workflow_lines = workflow_file.readlines()

    workflow_description = None
    for line in workflow_lines:

        if workflow_description is None:
            if line.startswith("# <!-- description -->"):
                workflow_description = ""
            continue

        if line.startswith("#"):
            workflow_description += f"{line.lstrip('#').strip()}\n"
            continue

        break

    return workflow_description


def analysed_workflow_inputs(workflow_inputs: dict) -> dict:
    """
    Analyse the inputs of the workflow and return the analysis results.
    """
    return {**workflow_inputs}


def analysed_workflow_outputs(workflow_outputs: dict) -> dict:
    """
    Analyse the outputs of the workflow and return the analysis results.
    """
    return {**workflow_outputs}


def analysed_workflow_secrets(workflow_secrets: dict) -> dict:
    """
    Analyse the outputs of the workflow and return the analysis results.
    """
    return {**workflow_secrets}


def analyse_workflow(workflow_path: str) -> dict:
    """
    Analyse the workflow file at the specified path and return the analysis results.
    """

    with open(workflow_path, mode="r", encoding="utf-8") as workflow_file:
        workflow = yaml.safe_load(stream=workflow_file)
        workflow_description = read_workflow_description(workflow_file=workflow_file)

    analysed_workflow = {"workflow_description": workflow_description}

    if "workflow_call" in workflow["on"]:
        analysed_workflow.update(
            {
                "is_reusable": True,
                "inputs": analysed_workflow_inputs(
                    workflow_inputs=workflow["on"]["workflow_call"].get("inputs", None)
                ),
                "outputs": analysed_workflow_outputs(
                    workflow_outputs=workflow["on"]["workflow_call"].get(
                        "outputs", None
                    )
                ),
                "secrets": analysed_workflow_secrets(
                    workflow_secrets=workflow["on"]["workflow_call"].get(
                        "secrets", None
                    )
                ),
            }
        )

    if "workflow_dispatch" in workflow["on"]:
        analysed_workflow.update(
            {
                "is_triggered_manually": True,
                "inputs": analysed_workflow_inputs(
                    workflow_inputs=workflow["on"]["workflow_dispatch"].get(
                        "inputs", None
                    )
                ),
            }
        )

    if "workflow_run" in workflow["on"]:
        analysed_workflow.update(
            {
                "is_triggered_by_execution_of_another_workflow": True,
                "triggered_by_execution_of_workflow": workflow["on"]["workflow_run"],
            }
        )


def generate_markdown(analysed_workflow: dict) -> str:
    """
    Generate a markdown documentation for the analysed workflow.
    """

    return ""


@app.command(name="generate")
def generate(
    workflow_path: str = typer.Argument(
        ..., help="The workflow to analyse and document."
    )
) -> None:
    """
    Generate a markdown documentation for the workflow file at the specified path.
    """

    print(f"Analysing workflow {workflow_path} ...")
    analysed_workflow = analyse_workflow(workflow_path=workflow_path)

    print(f"Generating markdown documentation for workflow {workflow_path} ...")
    doc_markdown = generate_markdown(analysed_workflow=analysed_workflow)

    with open(
        path.join(path.dirname(workflow_path), path.basename(workflow_path)),
        mode="w",
        encoding="utf-8",
    ) as generated_doc_file:
        generated_doc_file.write(doc_markdown)


if __name__ == "__main__":
    app()
