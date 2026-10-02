# Resume and maintain a research project

Read `PROJECT_STATE.md`, `project.json` and relevant `evidence.json` entries when present. Inspect only papers, code and artifacts needed for the next task. Do not repeat the whole literature review automatically.

## Resume
1. Compare recorded state with actual files and the user's latest instruction.
2. Verify the next step still applies; name discrepancies in files or assumptions.
3. Identify the smallest concrete next action and required evidence/runtime.
4. Execute authorized work, preserving user edits and existing tooling.
5. Update state after a meaningful checkpoint; never mark unexecuted tasks done.

If state is absent, infer a short provisional state from available material. Ask only about materially ambiguous objectives. Do not invent earlier decisions or results.

## State contents
Keep these concise:
- current objective, scope and task route;
- problem features and contribution class;
- completed artifacts and what was actually verified;
- decisions with reasons and source/run/claim IDs;
- open questions, blockers and rejected approaches;
- changed/relevant paths and the next concrete action.

Execution status differs from scientific interpretation. A compiled manuscript, completed run and supported claim are three different states.

## Evidence maintenance
Follow [project-contract](project-contract.md). Stable IDs connect text and notes to the same source, claim or run. Keep detailed reading, proof and experiment reasoning in its relevant note, not an oversized state file.

When sources, assumptions, implementation or data change, identify affected claims and mark them `needs_review` until checked. Do not inherit support from a different version/run. Preserve failures and abandoned-idea reasons.

Existing projects may use equivalent formats. Adapt rather than migrating all notes for a one-off task. Introduce this JSON contract when using bundled scripts or when a maintained project is requested.
