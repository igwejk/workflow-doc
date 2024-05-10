#!/usr/bin/env python

"""
Generate markdown documentation for a given GitHub Actions workflow. 

It includes the following functions:

- `workflowdoc()`: Command name.
- `read_workflow_description(workflow_file_content: str) -> str`:
  Reads the description of the workflow from the workflow file.
- `generate_markdown(workflow_path: str) -> Generator[str, None, None]`:
  Generates a markdown documentation for the analysed workflow.
- `generate(workflow_path: str) -> None`:
  Generates a markdown documentation for the workflow file at the specified path.
"""

from os import path
from pathlib import Path
from typing import Generator

import typer
import yaml


def workflowdoc() -> None:
    """
    This is a utility for documenting a given GitHub Actions workflow by analysing
    the workflow file and generating a markdown documentation.
    """


app = typer.Typer(callback=workflowdoc, name="workflowdoc")


def read_workflow_description(workflow_file_content: str) -> str:
    """
    Read the description of the workflow from the workflow file.
    """

    workflow_lines = workflow_file_content.split("\n")

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


def render_workflow_dispatch_input_type_md_table_cell(input_details: dict) -> str:
    """
    Render the markdown for the input type of the workflow dispatch input.
    """

    input_type = input_details.get("type")

    if input_type == "choice":
        input_options = input_details.get("options", [])
        input_options_li = "".join([f"<li>{option}</li>" for option in input_options])
        input_options_ul = f"<ul>{input_options_li}</ul>"

        return f"`{input_type}`:<br />{input_options_ul}"

    return f"`{input_type}`"


def generate_markdown(workflow_path: str) -> Generator[str, None, None]:
    """
    Generate a markdown documentation for the analysed workflow.
    """

    workflow_file_content = Path(workflow_path).read_text(encoding="utf-8")
    workflow = yaml.safe_load(workflow_file_content)

    yield f"# {workflow['name']}"
    yield "\n"
    yield read_workflow_description(workflow_file_content=workflow_file_content)
    yield "\n"

    yield "## Triggers"
    yield "\n"

    if "workflow_call" in workflow["on"]:
        yield "### `workflow_call`"
        yield "\n"
        yield "This workflow is reusable."
        yield "\n"

        if workflow["on"]["workflow_call"].get("inputs", None):
            yield "#### Inputs"
            yield "| Name | Description | Default | Required | Type |"
            yield "| :--- | :---------- | :------ | :------: | :--- |"

            for input_name, input_details in workflow["on"]["workflow_call"][
                "inputs"
            ].items():
                yield (
                    f"| {input_name} "
                    f"| {input_details.get('description', '')} "
                    f"| {input_details.get('default', '')} "
                    f"| {'*' if input_details.get('required', False) else ''} "
                    f"| `{input_details.get('type')}` |"
                )

        if workflow["on"]["workflow_call"].get("secrets", None):
            yield "#### Secrets"
            yield "| Name | Description | Required |"
            yield "| :--- | :---------- | :------: |"

            for secret_name, secret_details in workflow["on"]["workflow_call"][
                "secrets"
            ].items():
                yield (
                    f"| {secret_name} "
                    f"| {secret_details.get('description', '')} "
                    f"| {secret_details.get('required', False)} |"
                )

        if workflow["on"]["workflow_call"].get("outputs", None):
            yield "#### Outputs"
            yield "| Name | Description |"
            yield "| :--- | :---------- |"

            for output_name, output_details in workflow["on"]["workflow_call"][
                "outputs"
            ].items():
                yield (
                    f"| {output_name} " f"| {output_details.get('description', '')} |"
                )

    if "workflow_dispatch" in workflow["on"]:
        yield "### `workflow_dispatch`"
        yield "\n"
        yield "This workflow can be manually triggered."
        yield "\n"

        if workflow["on"]["workflow_dispatch"].get("inputs", None):
            yield "#### Inputs"
            yield "| Name | Description | Default | Required | Type |"
            yield "| :--- | :---------- | :------ | :------: | :--- |"

            for input_name, input_details in workflow["on"]["workflow_dispatch"][
                "inputs"
            ].items():
                type_table_value = render_workflow_dispatch_input_type_md_table_cell(
                    input_details=input_details
                )
                yield (
                    f"| {input_name} "
                    f"| {input_details.get('description', '')} "
                    f"| {input_details.get('default', '')} "
                    f"| {'*' if input_details.get('required', False) else ''} "
                    f"| {type_table_value} |"
                )

    if "workflow_run" in workflow["on"]:
        yield "### `workflow_run`"
        yield "\n"
        yield "This workflow is triggered by the execution of other workflows."
        yield "\n"

        yield "#### Triggering workflows:"
        yield "\n"
        for workflow_name in workflow["on"]["workflow_run"]["workflows"]:
            yield f"- {workflow_name}"
        yield "\n"

        branches = workflow["on"]["workflow_run"].get("branches", None) or workflow[
            "on"
        ]["workflow_run"].get("branches-ignore", None)
        if branches:
            yield (
                "#### Workflow branches:"
                if workflow["on"]["workflow_run"].get("branches", None)
                else "#### `Skipped` workflow branches:"
            )
            yield "\n"
            for branch in branches:
                yield f"- {branch}"
            yield "\n"

        yield "#### Workflow activity types:"
        activity_types = workflow["on"]["workflow_run"].get("types")
        for activity_type in activity_types:
            yield f"- {activity_type}"
        yield "\n"


@app.command(name="generate")
def generate(
    workflow_path: str = typer.Argument(
        ..., help="The workflow to analyse and document."
    )
) -> None:
    """
    Generate a markdown documentation for the workflow file at the specified path.
    """

    print(f"Generating markdown documentation for workflow {workflow_path} ...")
    generated_output_path = path.join(
        path.dirname(workflow_path), f"{path.basename(workflow_path)}.md"
    )

    with open(
        mode="wt", file=generated_output_path, encoding="utf-8"
    ) as generated_doc_file:

        for line in generate_markdown(workflow_path=workflow_path):
            print(line, file=generated_doc_file)

        generated_doc_file.flush()


if __name__ == "__main__":
    app()
