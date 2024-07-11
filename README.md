# GitHub Actions workflow docs

A CLI to generate documentation for a GitHub Actions workflow, based on the workflow definition and metadata included in the workflow as comments.

## Usage

### CLI

```bash
Usage: workflowdoc.py [OPTIONS] COMMAND [ARGS]...

This is a utility for documenting a given GitHub Actions workflow by analysing the workflow file and generating a markdown documentation.╮
│ --install-completion          Install completion for the current shell.                                                                │
│ --show-completion             Show completion for the current shell, to copy it or customize the installation.                         │
│ --help                        Show this message and exit.                                                                              │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ generate   Generate a markdown documentation for the workflow file at the specified path.                                              │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

Execute **`./workflowdoc.py generate /path/to/workflow.yaml`** to generate documentation for a workflow.

```bash
 Usage: workflowdoc.py generate [OPTIONS] WORKFLOW_PATH

 Generate a markdown documentation for the workflow file at the specified path.

╭─ Arguments ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    workflow_path      PATH  Path to the workflow to analyse and document.                                                            │
│                               [default: None]                                                                                          │
│                               [required]                                                                                               │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                                                                            │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

#### Executing `workflowdoc.py` in a container

If you have `Docker` available you may instead simplify the prerequisite setup by executing **`./workflowdoc.sh --help`**.

> [!IMPORTANT]
> Provide a **relative** path as argument to the script when using a container environment for execution.

### GitHub Action wrapper

Example:

```yaml
- id: generate-workflow-doc
  uses: igwejk/workflow-doc@v0
  with:
    path-to-workflow: /path/to/workflow.yaml
- run: |
    cat "${{ steps.generate-workflow-doc.outputs.path-to-generated-doc }}"
```

## License

This project is released under the [MIT License](./LICENSE).
