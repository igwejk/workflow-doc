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

    description = None
    for line in workflow_lines:
        if description is not None and line.startswith("#"):
            description += f"\n{line.lstrip('#').strip()}"
            continue

        
        if line.startswith("# <!-- description -->"):
            description += line.lstrip("#").strip()
        else:
            break

    return description


def analyse_workflow(workflow_path: str) -> dict:
    """
    Analyse the workflow file at the specified path and return the analysis results.
    """

    with open(workflow_path, mode="r", encoding="utf-8") as workflow_file:

        workflow = yaml.safe_load(workflow_file)
        workflow_description = read_workflow_description(workflow_file=workflow_file)

    return {}


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
