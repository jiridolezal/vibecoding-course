#!/usr/bin/env node
/**
 * PostToolUse(Edit|Write): run prettier on the file that was just written.
 * Silent no-op when prettier is not installed or the file is not ours.
 *
 * See local-bin.js for why this does not go through npx.
 */
const path = require("path");
const { runLocal } = require("./local-bin");

let raw = "";
process.stdin.on("data", (c) => (raw += c));
process.stdin.on("end", () => {
  let input;
  try {
    input = JSON.parse(raw);
  } catch {
    return process.exit(0);
  }

  const file = (input.tool_input || {}).file_path;
  if (!file || !/\.(ts|tsx|scss|json)$/.test(file)) return process.exit(0);
  const norm = file.split("\\").join("/");
  if (/\/(node_modules|lib|dist|temp|release)\//.test(norm)) return process.exit(0);
  if (/\.scss\.ts$/.test(file)) return process.exit(0);

  // Vendored files carry a provenance header saying not to edit them; keeping
  // them byte-identical to upstream is what makes a re-sync a diff.
  if (/\/src\/(theme\/(_|components\/)|utils\/cx\.ts)/.test(norm)) return process.exit(0);

  const root = process.env.CLAUDE_PROJECT_DIR || input.cwd || process.cwd();
  // Prettier is happy with an absolute path; passing it as an argv entry rather
  // than through a shell means a project path with a space is not a problem.
  runLocal(root, "prettier", ["--write", path.resolve(file)]);
  process.exit(0);
});
