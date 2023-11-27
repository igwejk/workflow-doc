# GitHub Actions workflow docs

<!-- BADGES/ -->
![example workflow](https://github.com/igwejk/workflow-docs/actions/workflows/ci.yml/badge.svg) [![npm](https://img.shields.io/npm/v/workflow-docs.svg)](https://npmjs.org/package/workflow-docs) [![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=workflow-docs&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=workflow-docs) [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=workflow-docs&metric=coverage)](https://sonarcloud.io/dashboard?id=workflow-docs)
<!-- /BADGES -->

A CLI to generate and update documentation for GitHub Actions workflow, based on the workflow definition and metadata included in the workflow as comments. To update your README in a GitHub workflow you can use the [workflow-docs-action](https://github.com/igwejk/workflow-docs-action).

## TL;DR

### Add the following comment blocks to your target `/path/to/README.md`

```markdown
<!-- workflow-docs-description -->

<!-- workflow-docs-inputs -->

<!-- workflow-docs-outputs -->

<!-- workflow-docs-runs -->
```

### Add a description to your target `/path/to/workflow.yml`

```yaml
# description:
# This workflows does things.
# With the inputs you provide it.
name: Workflow name
...
```

Optionally you can also add the following section to generate a usage guide, replacing \<project\> and \<version\> with the name and version of your project you would like to appear in your usage guide.

```markdown
<!-- workflow-docs-usage project="<project>" version="<version>" -->
```

### Generate docs via CLI

```bash
npm install -g workflow-docs
cd .github/workflows

# write docs to console
workflow-docs

# update readme
workflow-docs --update-readme
```

### Run the cli

```bash
workflow-docs -u
```

## CLI

### Options

The following options are available via the CLI

```text
Options:
      --help           Show help                                       [boolean]
      --version        Show version number                             [boolean]
  -t, --toc-level      TOC level used for markdown                     [number] [default: 2]
  -w, --workflow       GitHub Actions workflow file                    [string]
      --no-banner      Print no banner
  -u, --update-readme  Update readme file.                             [string]
  -l, --line-breaks    Used line breaks in the generated docs.
                          [string] [choices: "CR", "LF", "CRLF"] [default: "LF"]
```

### Update the README

workflow-docs can update your README based on the workflow definition and metadata included in the workflow as comments. The following sections can be updated: description, inputs, outputs and runs. Add the following tags to your README and run `workflow-docs --workflow /path/to/workflow.yml --update-readme /path/to/README.md`.

```markdown
<!-- workflow-docs-description -->

<!-- workflow-docs-inputs -->

<!-- workflow-docs-outputs -->

<!-- workflow-docs-runs -->
```

### Examples

#### Print workflow markdown docs to console

```bash
workflow-docs --workflow /path/to/workflow.yml
```

#### Update README.md

```bash
workflow-docs --workflow /path/to/workflow.yml --update-readme /path/to/README.md
```

#### Update readme and set TOC level 3

```bash
workflow-docs --workflow /path/to/workflow.yml --toc-level 3 --update-readme /path/to/README.md
```

## API

```javascript
import { generateWorkflowMarkdownDocs } from 'workflow-docs'

await generateWorkflowMarkdownDocs({
  workflowFile: '/path/to/workflow.yml'
  tocLevel: 2
  updateReadme: true
  readmeFile: 'README.md'
});
```

## Contribution

We welcome contributions, please checkout the [contribution guide](CONTRIBUTING.md).

## License

This project is released under the [MIT License](./LICENSE).
