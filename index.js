const { load: YAMLParse } = require("js-yaml");
const { readFile } = require("node:fs/promises");

async function generateWorkflowDocs({ workflowFile, lineBreaks, tocLevel }) {
  const workflowContent = await readFile(workflowFile, { encoding: "utf8" });
  const workflow = YAMLParse(workflowContent, { json: true });

  const inputs = generateInputsDocs(workflow.inputs);
}

async function generateWorkflowMarkdownDocs({
  workflowFile,
  updateReadme = false,
  readmeFile = "README.md",
  lineBreaks = "LF",
  tocLevel = 2,
} = {}) {
  const docs = await generateWorkflowDocs({
    workflowFile,
    lineBreaks,
    tocLevel,
  });

  if (updateReadme) {
    await updateReadmeFile({ readmeFile, docs });
  }

  const { description, inputs, outputs, triggers } = docs;

  return [description, inputs, outputs, triggers].join("\n\n");
}
