/**
 * Run a project-local CLI from a hook, portably.
 *
 * The obvious `execFileSync("npx.cmd", [...])` does not work on Windows: since
 * the CVE-2024-27980 fix, Node refuses to spawn a `.bat`/`.cmd` without
 * `shell: true` and throws EINVAL. A hook that treats that as a tool failure
 * blocks every stop with an empty error message; one that swallows it never
 * runs at all. Both were happening.
 *
 * `shell: true` is not the fix either - a shell does not quote the arguments
 * for you, so any project path containing a space breaks silently.
 *
 * So resolve the tool's JS entry point under node_modules and run it with the
 * Node binary already executing this hook. No shell, no `.cmd`, no quoting.
 */
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

// Entry points, newest packaging first. A tool that matches none is absent.
const ENTRIES = {
  tsc: ["typescript/bin/tsc"],
  eslint: ["eslint/bin/eslint.js"],
  stylelint: ["stylelint/bin/stylelint.mjs", "stylelint/bin/stylelint.js"],
  prettier: ["prettier/bin/prettier.cjs", "prettier/bin-prettier.js"],
};

/** Absolute path to a local tool's entry script, or null when not installed. */
const resolveLocalBin = (root, tool) => {
  for (const rel of ENTRIES[tool] || []) {
    const p = path.join(root, "node_modules", ...rel.split("/"));
    if (fs.existsSync(p)) return p;
  }
  return null;
};

/**
 * Run a local tool. Returns null on success or when the tool is not installed -
 * an absent toolchain is not a failure to report - and the combined output when
 * the tool exits non-zero.
 */
const runLocal = (root, tool, args, opts = {}) => {
  const bin = resolveLocalBin(root, tool);
  if (!bin) return null;
  try {
    execFileSync(process.execPath, [bin, ...args], {
      cwd: root,
      encoding: "utf8",
      stdio: ["ignore", "pipe", "pipe"],
      ...opts,
    });
    return null;
  } catch (e) {
    return `${e.stdout || ""}${e.stderr || ""}`.trim() || `${tool} ${args.join(" ")} failed`;
  }
};

module.exports = { resolveLocalBin, runLocal };
