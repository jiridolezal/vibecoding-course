#!/usr/bin/env node
/**
 * PreToolUse(Edit|Write): block hand-edits to version fields.
 *
 * package.json version, solution.version and features[].version must move
 * together. `scripts/set-version.js` is the only sanctioned writer - it uses
 * fs directly, so it never passes through this hook. There is deliberately no
 * environment-variable escape hatch: the model cannot set an env var for its
 * own Edit call, so an escape hatch would only block the skill that needs it.
 */
let raw = "";
process.stdin.on("data", (c) => (raw += c));
process.stdin.on("end", () => {
  let input;
  try {
    input = JSON.parse(raw);
  } catch {
    return process.exit(0);
  }

  const ti = input.tool_input || {};
  const file = (ti.file_path || "").split("\\").join("/");
  const isTarget =
    /\/package\.json$/.test(file) || /\/config\/package-solution\.json$/.test(file);
  if (!isTarget) return process.exit(0);

  // old_string counts too: an Edit that replaces `"version": "1.0.0"` names the
  // key on the way out even if the replacement does not.
  const payload = [ti.old_string, ti.new_string, ti.content].filter(Boolean).join("\n");

  const touchesVersionKey = /"version"\s*:/.test(payload);

  // A four-part literal only ever appears as solution.version or a feature
  // version, so it is decisive on its own. A three-part one is NOT: SPFx pins
  // most of its dependencies exactly, so `"1.23.2"` is what adding
  // @microsoft/sp-http looks like, and denying that would block ordinary work
  // with a message about version fields.
  const touchesSolutionVersion =
    /\/config\/package-solution\.json$/.test(file) && /"\d+\.\d+\.\d+\.\d+"/.test(payload);

  if (!touchesVersionKey && !touchesSolutionVersion) return process.exit(0);

  console.log(
    JSON.stringify({
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason:
          "Version fields are managed by scripts/set-version.js so package.json, " +
          "solution.version and features[].version stay in lockstep (x.y.z / x.y.z.0). " +
          "Run the spfx-version skill, which calls that script, instead of editing by hand.",
      },
    })
  );
  process.exit(0);
});
