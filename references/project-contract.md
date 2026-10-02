# Project data contract
Version 1. All JSON is UTF-8 and uses Python standard-library types. Paths are relative to the project root unless a source locator is an external URL. Reject project artifact paths escaping the project root.

## project.json
Required keys:
- schema_version: 1
- title: nonempty string
- direction: string (may be empty)
- author: string
- manuscript: {format: "ieee" | "article" | "markdown", main: relative path}
- experiment: {engine: "python" | "matlab" | "none", entrypoint: relative path or null, status: "not_configured" | "ready", seed: integer}
- research: {time_domain: string, dynamics: string array, objectives: string array, constraints: string array, contribution_type: string}
Default unspecified research fields are acceptable in a draft. Submission check is a structural aid, not a research-quality judgment.

## evidence.json
Root: {schema_version: 1, sources: [], claims: [], runs: []}.
All IDs are nonempty and unique across sources and runs. Claim IDs are unique.
sources entries:
{id, type: "literature" | "derivation" | "artifact", title, locator, verification: "unverified" | "metadata_verified" | "content_checked", bib_key: optional string}.
For local derivations/artifacts locator is a project-relative existing file; literature locator may be a URL/DOI or local file. A literature entry's content_checked means a human or agent read the relevant source; it is not proof of entailment.
claims entries:
{id, text, kind: "theory" | "empirical" | "literature" | "method" | "hypothesis", status: "hypothesis" | "needs_review" | "supported" | "rejected", in_manuscript: boolean, assumptions: string array, limitations: string array, evidence: [{evidence_id, locator}]}.
evidence_id refers to a source or run. locator is a nonempty precise pointer (page/theorem/equation/line or metric/figure/table), not just the source title.
Draft may have no claims or incomplete support. Submission requires every non-hypothesis in-manuscript claim to be supported with at least one evidence entry. Hypothesis-kind claims must have status hypothesis and must be explicitly labeled as such in prose; the latter is semantic review. Claims marked supported must not cite unverified/metadata-only sources or incomplete runs. Scripts only validate declared structure, never mathematical validity, novelty or sentence-level entailment.
runs entries:
{id, status: "not_run" | "completed" | "failed", config_path, code_revision, environment_path, seed, raw_data: string array, figures: string array}.
For completed runs config_path, environment_path and every raw_data/figure path must exist within project; code_revision nonempty, seed integer and at least one raw_data artifact required. Failed/not_run entries may have empty metadata and seed null; preserve them and describe reasons in experiment logs.

## Initial project files
project.json, evidence.json, PROJECT_STATE.md, notes/paper-cards.md, notes/directions.md, notes/theory-audit.md, notes/experiment-log.md, notes/claim-evidence.md.
Manuscript: paper/main.tex plus paper/sections/*.tex and paper/references.bib, OR paper/manuscript.md.
Engine: experiments/run_experiments.py OR experiments/run_experiments.m OR none. Skeletons must fail clearly until configured; no fabricated results, theorem or BibTeX citations.
Directories: experiments/configs, experiments/raw, experiments/results, paper/figures.
PROJECT_STATE.md captures task, done/open, decisions, relevant paths, next action; other notes start as instructions/empty tables, not research assertions.
Do not overwrite existing files by default. --force must back up every replaced file (including config) with a collision-safe backup directory inside project, and reject symlink/path-escape targets.

## Script interfaces
init_ieee_project.py PROJECT_DIR [--title TEXT] [--direction TEXT] [--author TEXT] [--format ieee|article|markdown] [--engine matlab|python|none] [--force]
Default format ieee and engine matlab for backwards compatibility. Main skill recommends explicit choices. Optional alias init_project.py if useful, not required.
check_project.py PROJECT_DIR [--mode draft|submission] [--json]
Default draft. Exit 0 no errors; 1 validation errors; 2 usage/unexpected operational issue if appropriate. Draft reports unresolved TODOs/unverified claims as warnings; submission errors. No requirement that every possible note be filled for all task routes.
build_paper.py PROJECT_DIR [--mode draft|submission]
Run structural check before build. In draft allow placeholders but do not report a ready-to-submit manuscript. Require latexmk for TeX. Submission reject undefined citations/references and missing citation keys, placeholders; warning checks must include generated TeX logs not just process status. Markdown produces clear no-PDF informational result, not pretend build.
build_ieee_pdf.sh PROJECT_DIR [additional arguments] thin compatibility wrapper to Python build.
