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

import re
from io import TextIOWrapper
from os import path
from typing import Generator

import typer
import yaml

YAML_RESERVED_TRUE = r"true|True|TRUE"
YAML_RESERVED_FALSE = r"false|False|FALSE"
YAML_RESERVED_NULL = r"null|Null|NULL"
YAML_RESERVED_YES = r"yes|Yes|YES"
YAML_RESERVED_NO = r"no|No|NO"
YAML_RESERVED_ON = r"on|On|ON"
YAML_RESERVED_OFF = r"off|Off|OFF"

YAML_RESERVED_WORDS = re.compile(
    rf"(^\s*)({YAML_RESERVED_TRUE}|{YAML_RESERVED_FALSE}|{YAML_RESERVED_NULL}"
    rf"|{YAML_RESERVED_YES}|{YAML_RESERVED_NO}|{YAML_RESERVED_ON}|{YAML_RESERVED_OFF}):"
)


def workflowdoc() -> None:
    """
    This is a utility for documenting a given GitHub Actions workflow by analysing
    the workflow file and generating a markdown documentation.
    """


app = typer.Typer(callback=workflowdoc, name="workflowdoc")


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


def render_mermaid_diagram(workflow: dict) -> list:
    """
    Generate a Mermaid diagram for the GitHub Actions workflow.
    """

    def get_job_entry_name(job_id, job):
        return job.get("name", word_separator.sub(" ", job_id))

    def get_state_diagram_content_for_job_labels(
        jobs_sorted_by_least_needs, indentation=4
    ):
        return [
            f"{' ' * indentation}{job_id}: {get_job_entry_name(job_id, job)}"
            for job_id, job in jobs_sorted_by_least_needs
        ]

    def get_state_diagram_content_for_job_steps(job, job_id, indentation=12):

        if "uses" in job:
            return [f"{' ' * indentation}Calls&nbsp;reusable&nbsp;workflow"]

        def get_step_label(step, job_id):

            prefix = job_id

            if "name" in step:
                step_label = step["name"].replace(" ", "&nbsp;")
            elif "uses" in step:
                step_label = step["uses"]
            elif "run" in step:
                step_label = step["run"][:10].replace("\n", "&nbsp;")
            else:
                step_label = step["id"]

            return f"{prefix}>>{step_label}"

        step_labels = [get_step_label(step, job_id) for step in job.get("steps", [])]
        step_transitions = []

        for index, step_label in enumerate(step_labels[1:], start=1):
            previous_step_label = step_labels[index - 1]
            step_transitions.append(
                f"{' ' * indentation}{previous_step_label} --> {step_label}"
            )

        return step_transitions or [f"{' ' * indentation}{step_labels[0]}"]

    def get_state_diagram_content_for_needs(job_id, job, indentation=8):
        if "needs" not in job:
            return []

        needed_job_ids = job["needs"]
        if isinstance(needed_job_ids, str):
            needed_job_ids = [needed_job_ids]

        return [
            f"{' ' * indentation}{needed_job_id} --> {job_id}"
            for needed_job_id in needed_job_ids
        ]

    def get_state_diagram_content_for_jobs(jobs_sorted_by_least_needs, indentation=8):

        state_diagram_content_for_jobs = [
            line
            for job_id, job in jobs_sorted_by_least_needs
            for line in [
                f"{' ' * indentation}[*] --> {job_id}",
                f"{' ' * indentation}state {job_id} {{",
                f"{' ' * (indentation+4)}direction TB",
                *get_state_diagram_content_for_job_steps(
                    job, job_id, indentation=indentation + 4
                ),
                f"{' ' * indentation}}}\n",
                *get_state_diagram_content_for_needs(
                    job_id, job, indentation=indentation
                ),
                f"\n{' ' * indentation}--",
            ]
        ]

        return (
            state_diagram_content_for_jobs[:-1]
            if "--" in state_diagram_content_for_jobs[-1]
            else state_diagram_content_for_jobs
        )

    word_separator = re.compile(r"[_-]")
    jobs_sorted_by_needs = sorted(
        workflow["jobs"].items(), key=lambda x: len(x[1].get("needs", []))
    )

    diagram = [
        "```mermaid",
        "\nstateDiagram-v2\n",
        *get_state_diagram_content_for_job_labels(jobs_sorted_by_needs, indentation=4),
        f"\n{' ' * 4}[*] --> Triggers",
        f"{' ' * 4}state Triggers {{\n",
        *get_state_diagram_content_for_jobs(jobs_sorted_by_needs, indentation=8),
        f"\n{' ' * 4}}}",
        "```",
    ]

    return diagram


def generate_markdown_from_workflow(
    workflow_lines: Generator[str, None, None]
) -> Generator[str, None, None]:
    """
    Generate a markdown documentation for the analysed workflow.
    """

    workflow_file_content = ""
    workflow_description = None

    # While reading the workflow description, collect the workflow content.
    for line in workflow_lines:
        workflow_file_content += line

        if workflow_description is None:
            if line.startswith("# <!-- description -->"):
                workflow_description = ""
            continue
        if line.startswith("#"):
            workflow_description += f"{line.lstrip('#').strip()}\n"
            continue

        workflow_description = workflow_description.rstrip("\n")
        break

    # Read the "rest" of the workflow content.
    workflow_file_content += "\n".join(workflow_lines)
    workflow = yaml.safe_load(workflow_file_content)

    yield f"# {workflow['name']}"
    yield f"\n{workflow_description}"

    yield "\n## Workflow Diagram\n"
    yield from render_mermaid_diagram(workflow)

    yield "\n## Triggers"
    if "workflow_call" in workflow["on"]:
        yield "\n### `workflow_call`"
        yield "\nThis workflow is reusable."

        if workflow["on"]["workflow_call"].get("inputs", None):
            yield "\n#### `workflow_call.inputs`\n"
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
            yield "\n#### Secrets\n"
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
            yield "\n#### Outputs\n"
            yield "| Name | Description |"
            yield "| :--- | :---------- |"

            for output_name, output_details in workflow["on"]["workflow_call"][
                "outputs"
            ].items():
                yield (
                    f"| {output_name} " f"| {output_details.get('description', '')} |"
                )

    if "workflow_dispatch" in workflow["on"]:
        yield "\n### `workflow_dispatch`"
        yield "\nThis workflow can be manually triggered."

        if workflow["on"]["workflow_dispatch"].get("inputs", None):
            yield "\n#### `workflow_dispatch.inputs`\n"
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
        yield "\n### `workflow_run`"
        yield "\nThis workflow is triggered by the execution of other workflows."

        yield "\n#### `workflow_run.workflows`\n"
        yield from [
            f"- {workflow_name}"
            for workflow_name in workflow["on"]["workflow_run"]["workflows"]
        ]

        branches = workflow["on"]["workflow_run"].get("branches", None) or workflow[
            "on"
        ]["workflow_run"].get("branches-ignore", None)
        if branches:
            yield (
                "\n#### `workflow_run.branches`\n"
                if workflow["on"]["workflow_run"].get("branches", None)
                else "\n#### `workflow_run.branches-ignore`\n"
            )
            yield from [f"- {branch}" for branch in branches]

        yield "\n#### `workflow_run.types`\n"
        activity_types = workflow["on"]["workflow_run"].get("types")
        yield from [f"- {activity_type}" for activity_type in activity_types]


def generate_normalised_yaml(yaml_file: TextIOWrapper) -> Generator[str, None, None]:
    """
    Generate lines of normalised YAML file content.
    """

    yaml_file.seek(0)

    for line in yaml_file:
        yield YAML_RESERVED_WORDS.sub(r'\1"\2":', line)


@app.command(name="generate")
def generate(
    workflow_path: str = typer.Argument(
        ..., help="The workflow to analyse and document."
    )
) -> None:
    """
    Generate a markdown documentation for the workflow file at the specified path.
    """

    print(f"Processing workflow {workflow_path} ...\n.\n.\n.\n")

    generated_output_path = path.join(
        path.dirname(workflow_path), f"{path.basename(workflow_path)}.md"
    )
    print(f"Generating documentation at {generated_output_path} ...\n.\n.\n.\n")

    with (
        open(file=workflow_path, mode="rt", encoding="utf-8") as workflow_file,
        open(
            mode="wt", file=generated_output_path, encoding="utf-8"
        ) as generated_doc_file,
    ):

        for line in generate_markdown_from_workflow(
            workflow_lines=generate_normalised_yaml(yaml_file=workflow_file)
        ):
            print(line, file=generated_doc_file)

        generated_doc_file.flush()


if __name__ == "__main__":
    app()
