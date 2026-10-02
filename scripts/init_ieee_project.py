#!/usr/bin/env python3
"""Create a safe, configurable control-research project (Python standard library)."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile


DEFAULTS = {
    "title": "Control Research Manuscript",
    "direction": "",
    "author": "Author Name",
    "format": "ieee",
    "engine": "matlab",
}
DIRECTORIES = (
    "notes", "experiments/configs", "experiments/raw", "experiments/results",
    "paper/figures",
)


def latex_escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
        "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
        "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in value)


def json_text(value: object) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def check_no_symlinks(path: Path) -> None:
    """Reject links including dangling links, before resolving or writing paths."""
    for component in reversed((path, *path.parents)):
        if component.is_symlink():
            raise ValueError(f"Symlink paths are not allowed: {component}")


def safe_target(root: Path, relative: str, *, directory: bool = False) -> Path:
    part = Path(relative)
    if part.is_absolute() or ".." in part.parts:
        raise ValueError(f"Path must stay inside the project: {relative}")
    target = root / part
    check_no_symlinks(target)
    for parent in target.parents:
        if parent.exists() and not parent.is_dir():
            raise ValueError(f"Expected a directory: {parent}")
    if target.exists() and (not target.is_dir() if directory else not target.is_file()):
        raise ValueError(f"Expected a {'directory' if directory else 'regular file'}: {target}")
    return target


def read_existing_config(root: Path, force: bool) -> dict:
    target = safe_target(root, "project.json")
    if not target.exists():
        return {}
    try:
        value = json.loads(target.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError("project.json must contain an object")
        return value
    except (ValueError, UnicodeError) as error:
        if force:
            return {}
        raise ValueError(f"Cannot read existing project.json: {error}. Restore it or use --force (backs up files).") from error


def choices(args: argparse.Namespace, existing: dict) -> dict:
    old = {
        "title": existing.get("title"), "direction": existing.get("direction"),
        "author": existing.get("author"),
        "format": existing.get("manuscript", {}).get("format") if isinstance(existing.get("manuscript"), dict) else None,
        "engine": existing.get("experiment", {}).get("engine") if isinstance(existing.get("experiment"), dict) else None,
    }
    result = {}
    for name, default in DEFAULTS.items():
        requested = getattr(args, name)
        previous = old[name]
        if requested is not None and previous is not None and requested != previous and not args.force:
            raise ValueError(f"Existing {name} is {previous!r}; use --force to change it with backups.")
        result[name] = requested if requested is not None else previous if isinstance(previous, str) else default
    if not result["title"].strip():
        raise ValueError("Title must not be empty.")
    if result["format"] not in ("ieee", "article", "markdown") or result["engine"] not in ("python", "matlab", "none"):
        raise ValueError("Existing project format or engine is unsupported; provide explicit choices with --force.")
    return result


def project_files(options: dict, existing: dict) -> dict[str, str]:
    title, direction, author = (options[key] for key in ("title", "direction", "author"))
    form, engine = options["format"], options["engine"]
    entrypoint = None if engine == "none" else f"experiments/run_experiments.{'py' if engine == 'python' else 'm'}"
    config = {
        "schema_version": 1, "title": title, "direction": direction, "author": author,
        "manuscript": {"format": form, "main": "paper/manuscript.md" if form == "markdown" else "paper/main.tex"},
        "experiment": {"engine": engine, "entrypoint": entrypoint, "status": "not_configured", "seed": 0},
        "research": {
            "time_domain": "", "dynamics": [], "objectives": [], "constraints": [],
            "contribution_type": "",
        },
    }
    if isinstance(existing.get("research"), dict):
        config["research"].update(existing["research"])
    files = {
        "project.json": json_text(config),
        "evidence.json": json_text({"schema_version": 1, "sources": [], "claims": [], "runs": []}),
        "PROJECT_STATE.md": """# Project state

## Current task
Choose the requested task: read, select direction, audit theory, reproduce, design/run experiments, write/revise, or resume.

## Done
- Project scaffold created; no research result has been generated or validated.

## Open items
- Record the system class, objectives, constraints, and contribution type in project.json.
- Identify the available source papers, derivations, code, and data.

## Decisions
Record date, decision, reason, evidence ID, and consequences here.

## Relevant paths
- project.json: project and experiment settings.
- evidence.json: sources, claims, and runs with precise evidence locators.
- notes/: reading, direction, theory, experiment, and claim records.
- paper/: editable manuscript; experiments/: configuration and actual run artifacts.

## Next action
State one concrete action and the input it needs. Read only the files relevant to that task.
""",
        "notes/paper-cards.md": """# Paper cards

Use one card per source. Record source ID, title, authors, year, DOI/URL/local path, version, and reading coverage (full / partial / abstract only).

For each card record the problem, system model, information available to the controller, assumptions, mechanism and design rationale, theorem statements, key proof steps, and empirical setup. Give page/section/equation/theorem locators for each important claim. Separate the source's conclusions from your interpretation.

Record limitations, missing evidence, and transfer conditions. Mark candidate extensions as hypotheses until checked against closest work. Metadata verification alone does not establish that a paper supports a sentence.

| Source ID | Coverage/version | Key claim and precise locator | Assumptions/limitations | Transfer conditions |
|---|---|---|---|---|
""",
        "notes/directions.md": """# Candidate directions

Begin with provisional gaps, then search the closest competing work before choosing a direction. No fixed number of candidates or publisher quota is required.

Prefer qualitative judgments supported by evidence; numerical scores are optional. Use unknown when evidence is missing. If scores are used, state the scale, weights, and rationale, and keep critical blockers separate from totals. No score establishes novelty.

| Candidate | Problem value | Distinctness | Technical plausibility | Validation quality | Feasibility | Scope and cost | Robustness of contribution | Closest work / uncertainty |
|---|---|---|---|---|---|---|---|---|

Problem value: who benefits and why the limitation matters. Distinctness: the remaining difference after inspecting closest work. Technical plausibility: a credible mechanism or proof route and its obstacle. Validation quality: falsifiable claims and fair evaluation. Feasibility: available data, platforms, skills, time, and compute. Scope and cost: a bounded minimal contribution, dependencies, effort, and risks. Robustness of contribution: what remains useful if the strongest claim fails.

For each serious candidate record the contribution type (theory / algorithm / engineering / data-tool), explicit difference from the closest work, minimal validation, falsification condition, required resources, and next decision. A useful engineering or data contribution need not invent a theorem. Never guarantee publication.
""",
        "notes/theory-audit.md": """# Theory audit

Record system features, time domain, solution concept, controller information, disturbances, constraints, and the exact scope of each conclusion. Choose applicable obligations; do not force all branches onto every paper.

| Claim ID | Statement / source locator | Assumptions used | Proof obligations / missing steps | Status | Suggested correction |
|---|---|---|---|---|---|

Check well-posedness and dimensions, quantifiers, domains, equilibrium or target set, invariance/feasibility, regularity, and the step connecting each inequality to the asserted guarantee. Distinguish stability, attraction, convergence rate, boundedness, expected/probabilistic guarantees, safety, and finite-horizon performance. Check sampling, delays, uncertainty and solver assumptions where applicable.

Record unresolved gaps honestly. Numerical examples and symbolic checks can reveal problems but do not replace a complete proof. Keep original, proposed correction, and supporting derivation distinct.
""",
        "notes/experiment-log.md": """# Experiment log

No experiment has been run. Implement an actual model/controller and baselines before setting experiment.status to ready. The generated entrypoint deliberately fails until implemented.

Before each run, record the hypothesis, metric definitions/units, common information and actuation limits, disturbance/sampling protocol, baseline tuning budget, development versus held-out cases, and stopping or falsification rule.

| Run ID | Status | Config / code revision / environment | Seed and initial conditions | Raw data / metrics / figures | Outcome or failure reason |
|---|---|---|---|---|---|

Store actual inputs and solver settings in experiments/configs, raw outputs in experiments/raw, and derived results in experiments/results. Add complete provenance to evidence.json. Preserve failed runs and report neutral or unfavorable outcomes. Do not synthesize a favorable trajectory or describe an unexecuted run as verified.
""",
        "notes/claim-evidence.md": """# Claim and evidence review

Keep evidence.json as the machine-readable record. Assign stable source, claim, and run IDs. Each evidence link needs a precise locator: page/theorem/equation/line or run metric/figure/table.

| Claim ID | Exact manuscript statement / location | Kind and status | Evidence ID + precise locator | Assumptions / limitations | Review action |
|---|---|---|---|---|---|

Review separately: source exists; metadata is correct; relevant content was read; content supports this exact sentence; scope and assumptions match. A script can check structure and referenced artifacts, not novelty, mathematical validity, or semantic entailment. Hypotheses must be labeled explicitly in prose.
""",
    }
    section_specs = [
        ("introduction", "Introduction", "State the problem, closest work, precise contribution, and evidence-backed scope."),
        ("related_work", "Related Work", "Compare the closest methods under matched assumptions; insert verified citations only."),
        ("problem_formulation", "Problem Formulation", "Define the system, variables, information, assumptions, constraints, and objective."),
        ("main_results", "Main Results", "Present the actual contribution and evidence. Add a theorem only when a proof and assumptions are available."),
        ("algorithm", "Method", "Specify implementable steps, inputs, parameters, complexity, and applicable conditions."),
        ("simulation", "Validation", "Report actual experiments or other appropriate validation, fair comparisons, provenance, and failures."),
        ("conclusion", "Conclusion", "State supported findings, limitations, and unresolved questions."),
    ]
    if form == "markdown":
        files["paper/manuscript.md"] = f"# {title}\n\n{author}\n\n## Abstract\n\nTODO: Summarize only established findings.\n\n" + "\n\n".join(f"## {heading}\n\nTODO: {prompt}" for _, heading, prompt in section_specs) + "\n\n## References\n\nTODO: Add verified sources with precise in-text attribution.\n"
    else:
        document_class = r"\documentclass[conference]{IEEEtran}" if form == "ieee" else r"\documentclass[11pt]{article}"
        files["paper/main.tex"] = document_class + "\n" + (r"\usepackage[margin=1in]{geometry}" + "\n" if form == "article" else "") + r"""\usepackage{amsmath,amssymb,graphicx}
\begin{document}
""" + f"\\title{{{latex_escape(title)}}}\n\\author{{{latex_escape(author)}}}\n\\maketitle\n" + r"""\begin{abstract}
\input{sections/abstract}
\end{abstract}
""" + "".join(f"\\input{{sections/{name}}}\n" for name, _, _ in section_specs) + f"% Enable after adding verified citation keys and using them in the text:\n% \\bibliographystyle{{{'IEEEtran' if form == 'ieee' else 'plain'}}}\n% \\bibliography{{references}}\n\\end{{document}}\n"
        files["paper/sections/abstract.tex"] = "TODO: Summarize only established findings.\n"
        for name, heading, prompt in section_specs:
            files[f"paper/sections/{name}.tex"] = f"\\section{{{heading}}}\nTODO: {prompt}\n"
        files["paper/references.bib"] = ""
    if engine != "none":
        files["experiments/configs/base.json"] = json_text({
            "schema_version": 1, "seed": 0, "configured": False,
            "model": {}, "controller": {}, "baselines": [], "solver": {},
            "scenarios": [], "metrics": [], "held_out_scenarios": [],
        })
    if engine == "python":
        files[entrypoint] = '''#!/usr/bin/env python3
"""Research experiment entrypoint. No model, controller, or results are supplied."""
from pathlib import Path
import json


def main():
    project_root = Path(__file__).resolve().parents[1]
    config_path = project_root / "experiments" / "configs" / "base.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    # Implement the actual model, methods, fair baselines and metrics here.
    # Save configuration, environment, raw data, and failures for each real run.
    # Setting configured=true alone does not supply an implementation.
    raise SystemExit(
        "Experiment is not configured: implement the research model and methods "
        f"before running (config: {config_path}, seed: {config['seed']})."
    )


if __name__ == "__main__":
    main()
'''
    elif engine == "matlab":
        files[entrypoint] = '''% Research experiment entrypoint; no model, controller, or results supplied.
project_root = fileparts(fileparts(mfilename('fullpath')));
config_path = fullfile(project_root, 'experiments', 'configs', 'base.json');
config = jsondecode(fileread(config_path));
% Implement actual dynamics, methods, fair baselines and metric definitions.
% Record the configuration, solver/environment, raw data and failures per run.
% Setting configured=true alone does not supply an implementation.
error('sci_writing:NotConfigured', ...
    'Experiment is not configured: implement the research model and methods first. Config: %s; seed: %d', ...
    config_path, config.seed);
'''
    return files


def atomic_write(target: Path, content: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    check_no_symlinks(target)
    descriptor, temporary_name = tempfile.mkstemp(prefix=".sci-writing-", dir=target.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


def initialize(args: argparse.Namespace) -> tuple[int, int, Path | None]:
    root = Path(os.path.abspath(os.path.expanduser(args.project_dir)))
    check_no_symlinks(root)
    if root.exists() and not root.is_dir():
        raise ValueError(f"Project path is not a directory: {root}")
    existing = read_existing_config(root, args.force)
    options = choices(args, existing)
    files = project_files(options, existing)
    # Complete the safety preflight before creating or modifying any files.
    for relative in DIRECTORIES:
        safe_target(root, relative, directory=True)
    targets = {relative: safe_target(root, relative) for relative in files}
    safe_target(root, ".sci-writing-backups", directory=True)
    replaced = [relative for relative, target in targets.items() if target.exists()]
    root.mkdir(parents=True, exist_ok=True)
    backup = None
    if args.force and replaced:
        backup_root = safe_target(root, ".sci-writing-backups", directory=True)
        backup_root.mkdir(exist_ok=True)
        prefix = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S-%fZ-")
        backup = Path(tempfile.mkdtemp(prefix=prefix, dir=backup_root))
        # Finish ALL backups before replacing the first existing file.
        for relative in replaced:
            source = safe_target(root, relative)
            destination = backup / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
    for relative in DIRECTORIES:
        safe_target(root, relative, directory=True).mkdir(parents=True, exist_ok=True)
    written = skipped = 0
    for relative, content in files.items():
        target = safe_target(root, relative)
        if target.exists() and not args.force:
            skipped += 1
            continue
        atomic_write(target, content)
        written += 1
    return written, skipped, backup


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", help="New or existing project directory")
    for name in ("title", "direction", "author"):
        parser.add_argument(f"--{name}", help=f"Project {name} (new-project default: {DEFAULTS[name]!r})")
    parser.add_argument("--format", choices=("ieee", "article", "markdown"), help="Manuscript format (new-project default: ieee)")
    parser.add_argument("--engine", choices=("matlab", "python", "none"), help="Experiment engine (new-project default: matlab)")
    parser.add_argument("--force", action="store_true", help="Replace managed files after backing up every existing target")
    args = parser.parse_args(argv)
    try:
        written, skipped, backup = initialize(args)
    except (OSError, ValueError) as error:
        print(f"Initialization failed: {error}", file=sys.stderr)
        return 2
    print(f"Project initialized: {written} files written, {skipped} existing files preserved.")
    if backup is not None:
        print(f"Backups: {backup}")
    print("Draft scaffold only; configure the research and supply real evidence before claiming results.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
