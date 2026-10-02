#!/usr/bin/env python3
"""Build a manuscript with explicit draft/submission structural checks."""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import shutil
import subprocess
import sys

from check_project import Checker, print_result, resolve_project


UNDEFINED = re.compile(
    r"(?:LaTeX(?:\s+Warning)?[^\n]*?(?:Citation|Reference)[^\n]*?undefined|"
    r"(?:There were|has) undefined (?:references|citations)|"
    r"Package (?:natbib|biblatex) Warning:[^\n]*(?:undefined|not found)|"
    r"I didn't find a database entry for|Warning--I didn't find a database entry for|"
    r"undefined (?:references|citations))", re.I)


def dependency_message(output):
    if re.search(r"(?:File\s+[`']?IEEEtran\.cls['`]?\s+not found|IEEEtran\.cls.*not found)", output, re.I):
        return "Missing IEEEtran.cls. Install the IEEEtran package in your TeX distribution, or initialize an article-format project for a generic draft."
    return None


def build(project_dir, mode="draft"):
    root = resolve_project(project_dir)
    if not (root / "project.json").is_file():
        print("ERROR: project.json is missing. Older standalone paper folders require project configuration; initialize a new project and migrate the manuscript before using this builder.")
        return 1
    checker = Checker(root, mode)
    result = checker.run()
    print_result(result)
    if not result["ok"]:
        return 1
    manuscript = checker.project["manuscript"]
    if manuscript["format"] == "markdown":
        print("Markdown manuscript checked. No PDF was built; use an explicitly selected document export workflow when a PDF is required.")
        return 0
    latexmk = shutil.which("latexmk")
    if not latexmk:
        print("ERROR: latexmk is unavailable. Install latexmk and a TeX distribution, then rerun this command.")
        return 2
    source = checker.manuscript_files[0]
    output_dir = source.parent / "build"
    # Reject symlinked build directories that could write outside this project.
    if not output_dir.resolve().is_relative_to(root):
        print("ERROR: build output directory escapes the project root.")
        return 1
    output_dir.mkdir(parents=True, exist_ok=True)
    command = [latexmk, "-pdf", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error", "-no-shell-escape", "-outdir=build", source.name]
    try:
        proc = subprocess.run(command, cwd=source.parent, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8", errors="replace", check=False)
    except OSError as exc:
        print(f"ERROR: Could not run latexmk: {exc}")
        return 2
    print(proc.stdout, end="" if proc.stdout.endswith("\n") else "\n")
    log_file = output_dir / (source.stem + ".log")
    log = log_file.read_text(encoding="utf-8", errors="replace") if log_file.is_file() else ""
    bib_log = output_dir / (source.stem + ".blg")
    if bib_log.is_file():
        log += "\n" + bib_log.read_text(encoding="utf-8", errors="replace")
    diagnostic = dependency_message(proc.stdout + "\n" + log)
    if diagnostic:
        print("ERROR: " + diagnostic)
    if proc.returncode:
        print(f"ERROR: latexmk failed with exit status {proc.returncode}; inspect {log_file}.")
        return 1
    # latexmk may print transient first-pass warnings that disappear after reruns.
    # The final log is authoritative; stdout is only a fallback if no log exists.
    unresolved = UNDEFINED.search(log if log_file.is_file() else proc.stdout)
    if unresolved:
        prefix = "ERROR" if mode == "submission" else "WARNING"
        print(f"{prefix}: TeX reports unresolved citations or references: {unresolved.group(0)}")
        if mode == "submission":
            return 1
    pdf = output_dir / (source.stem + ".pdf")
    if not pdf.is_file():
        print("ERROR: latexmk returned success but the expected PDF is missing.")
        return 1
    print(f"PDF built: {pdf}")
    if mode == "draft":
        print("Draft output; a successful build does not establish submission readiness.")
    else:
        print("Submission structural/build checks passed. Research validity and journal requirements still require review.")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("--mode", choices=("draft", "submission"), default="draft")
    args = parser.parse_args(argv)
    try:
        return build(args.project_dir, args.mode)
    except (OSError, UnicodeError) as exc:
        print(f"ERROR: Build operation failed: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
