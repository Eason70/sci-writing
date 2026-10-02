#!/usr/bin/env python3
"""Check declared project structure and evidence links, not research validity."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


class Checker:
    def __init__(self, root: Path, mode: str = "draft"):
        self.root = root.resolve()
        self.mode = mode
        self.issues: list[dict[str, str]] = []
        self.project: dict = {}
        self.manuscript_files: list[Path] = []
        self.bib_keys: set[str] = set()

    def add(self, level: str, code: str, message: str):
        self.issues.append({"level": level, "code": code, "message": message})

    def unresolved(self, code: str, message: str):
        self.add("error" if self.mode == "submission" else "warning", code, message)

    def string(self, value, where, nonempty=True):
        if not isinstance(value, str) or (nonempty and not value.strip()):
            self.add("error", "schema", f"{where}: expected {'nonempty ' if nonempty else ''}string")
            return False
        return True

    def enum(self, value, options, where):
        if not isinstance(value, str) or value not in options:
            self.add("error", "schema", f"{where}: expected one of {', '.join(options)}")
            return False
        return True

    def array(self, value, where):
        if not isinstance(value, list):
            self.add("error", "schema", f"{where}: expected array")
            return []
        return value

    def strings(self, value, where):
        values = self.array(value, where)
        for i, item in enumerate(values):
            self.string(item, f"{where}[{i}]")
        return values

    def object(self, value, where):
        if not isinstance(value, dict):
            self.add("error", "schema", f"{where}: expected object")
            return {}
        return value

    def integer(self, value, where):
        if type(value) is not int:
            self.add("error", "schema", f"{where}: expected integer (not boolean)")
            return False
        return True

    def path(self, value, where, exists=True, base=None):
        if not self.string(value, where):
            return None
        candidate = Path(value)
        # Check both operating-system syntaxes, including Windows drives/UNC on Unix.
        if candidate.is_absolute() or re.match(r"^[A-Za-z]:", value) or value.startswith("\\"):
            self.add("error", "path_escape", f"{where}: must be project-relative: {value}")
            return None
        if "\\" in value:
            candidate = Path(value.replace("\\", "/"))
        try:
            resolved = ((base or self.root) / candidate).resolve()
        except (OSError, ValueError, RuntimeError) as exc:
            self.add("error", "invalid_path", f"{where}: invalid path: {exc}")
            return None
        if not resolved.is_relative_to(self.root):
            self.add("error", "path_escape", f"{where}: escapes project root: {value}")
            return None
        if exists and not resolved.is_file():
            self.add("error", "missing_file", f"{where}: file does not exist: {value}")
            return None
        return resolved

    def read_json(self, filename):
        path = self.path(filename, filename)
        if path is None:
            return {}
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            self.add("error", "invalid_json", f"{filename}: {exc}")
            return {}
        obj = self.object(value, filename)
        if type(obj.get("schema_version")) is not int or obj.get("schema_version") != 1:
            self.add("error", "schema", f"{filename}.schema_version: expected integer 1")
        return obj

    def check_config(self):
        p = self.project = self.read_json("project.json")
        self.string(p.get("title"), "project.title")
        for key in ("direction", "author"):
            self.string(p.get(key), f"project.{key}", nonempty=False)
        m = self.object(p.get("manuscript"), "project.manuscript")
        self.enum(m.get("format"), ("ieee", "article", "markdown"), "manuscript.format")
        main = self.path(m.get("main"), "manuscript.main")
        expected = ".md" if m.get("format") == "markdown" else ".tex"
        if main is not None and main.suffix.lower() != expected:
            self.add("error", "manuscript_format", f"manuscript.main: {m.get('format')} requires {expected}")
        e = self.object(p.get("experiment"), "project.experiment")
        self.enum(e.get("engine"), ("python", "matlab", "none"), "experiment.engine")
        self.enum(e.get("status"), ("not_configured", "ready"), "experiment.status")
        self.integer(e.get("seed"), "experiment.seed")
        if e.get("engine") == "none":
            if e.get("entrypoint") is not None:
                self.add("error", "schema", "experiment.entrypoint must be null when engine is none")
        else:
            self.path(e.get("entrypoint"), "experiment.entrypoint")
        r = self.object(p.get("research"), "project.research")
        self.string(r.get("time_domain"), "research.time_domain", False)
        self.string(r.get("contribution_type"), "research.contribution_type", False)
        for key in ("dynamics", "objectives", "constraints"):
            self.strings(r.get(key), f"research.{key}")
        return main

    def check_evidence(self):
        manifest = self.read_json("evidence.json")
        evidence = {}
        for i, value in enumerate(self.array(manifest.get("sources"), "sources")):
            where = f"sources[{i}]"
            source = self.object(value, where)
            sid = source.get("id")
            if self.string(sid, f"{where}.id"):
                if sid in evidence:
                    self.add("error", "duplicate_id", f"Duplicate evidence ID: {sid}")
                else:
                    evidence[sid] = source
            self.enum(source.get("type"), ("literature", "derivation", "artifact"), f"{where}.type")
            self.string(source.get("title"), f"{where}.title")
            self.enum(source.get("verification"), ("unverified", "metadata_verified", "content_checked"), f"{where}.verification")
            loc = source.get("locator")
            if self.string(loc, f"{where}.locator"):
                external = is_external_locator(loc)
                if external and source.get("type") != "literature":
                    self.add("error", "source_locator", f"{where}: derivation/artifact locator must be a local file")
                elif not external:
                    self.path(loc, f"{where}.locator")
            if "bib_key" in source:
                self.string(source["bib_key"], f"{where}.bib_key")
        for i, value in enumerate(self.array(manifest.get("runs"), "runs")):
            where = f"runs[{i}]"
            run = self.object(value, where)
            rid = run.get("id")
            if self.string(rid, f"{where}.id"):
                if rid in evidence:
                    self.add("error", "duplicate_id", f"Duplicate evidence ID: {rid}")
                else:
                    evidence[rid] = run
            self.enum(run.get("status"), ("not_run", "completed", "failed"), f"{where}.status")
            completed = run.get("status") == "completed"
            for key in ("config_path", "environment_path"):
                path = run.get(key)
                if self.string(path, f"{where}.{key}", nonempty=completed) and path:
                    self.path(path, f"{where}.{key}", exists=completed)
            self.string(run.get("code_revision"), f"{where}.code_revision", nonempty=completed)
            if completed or run.get("seed") is not None:
                self.integer(run.get("seed"), f"{where}.seed")
            elif "seed" not in run:
                self.add("error", "schema", f"{where}.seed: required (null permitted for incomplete runs)")
            for key in ("raw_data", "figures"):
                artifacts = self.strings(run.get(key), f"{where}.{key}")
                if completed and key == "raw_data" and not artifacts:
                    self.add("error", "run_incomplete", f"{where}: completed run requires raw_data")
                for j, artifact in enumerate(artifacts):
                    if isinstance(artifact, str) and artifact:
                        self.path(artifact, f"{where}.{key}[{j}]", exists=completed)
        claim_ids = set()
        for i, value in enumerate(self.array(manifest.get("claims"), "claims")):
            where = f"claims[{i}]"
            claim = self.object(value, where)
            cid = claim.get("id")
            if self.string(cid, f"{where}.id"):
                if cid in claim_ids:
                    self.add("error", "duplicate_id", f"Duplicate claim ID: {cid}")
                claim_ids.add(cid)
            self.string(claim.get("text"), f"{where}.text")
            self.enum(claim.get("kind"), ("theory", "empirical", "literature", "method", "hypothesis"), f"{where}.kind")
            self.enum(claim.get("status"), ("hypothesis", "needs_review", "supported", "rejected"), f"{where}.status")
            if type(claim.get("in_manuscript")) is not bool:
                self.add("error", "schema", f"{where}.in_manuscript: expected boolean")
            for key in ("assumptions", "limitations"):
                self.strings(claim.get(key), f"{where}.{key}")
            links = self.array(claim.get("evidence"), f"{where}.evidence")
            if claim.get("kind") == "hypothesis" and claim.get("status") != "hypothesis":
                self.add("error", "claim_status", f"{where}: hypothesis kind requires hypothesis status")
            if claim.get("in_manuscript") is True and claim.get("kind") != "hypothesis":
                if claim.get("status") != "supported" or not links:
                    self.unresolved("unsupported_claim", f"{where} ({cid}): manuscript claim needs supported status and evidence")
            if claim.get("status") == "supported" and not links:
                self.add("error", "unsupported_claim", f"{where}: supported claim requires evidence")
            for j, value in enumerate(links):
                lw = f"{where}.evidence[{j}]"
                link = self.object(value, lw)
                eid = link.get("evidence_id")
                self.string(link.get("locator"), f"{lw}.locator")
                if not self.string(eid, f"{lw}.evidence_id"):
                    continue
                if eid not in evidence:
                    self.add("error", "missing_evidence", f"{lw}: unknown evidence ID {eid}")
                    continue
                item = evidence[eid]
                if claim.get("status") == "supported":
                    verified = item.get("verification") == "content_checked" if "type" in item else item.get("status") == "completed"
                    if not verified:
                        self.add("error", "unverified_support", f"{where}: supported claim cites unverified or incomplete evidence {eid}")

    def read_text(self, path):
        try:
            return path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            self.add("error", "read_error", f"{path.relative_to(self.root)}: {exc}")
            return ""

    def placeholders(self, text, path):
        for number, line in enumerate(text.splitlines(), 1):
            if re.search(r"\b(?:TODO|TBD|FIXME|PLACEHOLDER|REPLACE_ME)\b|\\todo\b", line, re.IGNORECASE):
                self.unresolved("placeholder", f"{path.relative_to(self.root)}:{number}: unresolved placeholder")

    def tex_target(self, raw, base, suffix, where):
        if "\\" in raw or "#" in raw:
            self.unresolved("dynamic_tex_path", f"{where}: cannot statically resolve TeX path {raw!r}; review manually")
            return None
        value = raw if Path(raw).suffix else raw + suffix
        return self.path(value, where, base=base)

    def check_manuscript(self, main):
        if main is None:
            return
        if self.project.get("manuscript", {}).get("format") == "markdown":
            contents = self.read_text(main)
            # HTML comments are instructions rather than manuscript assertions.
            self.placeholders(re.sub(r"<!--.*?-->", "", contents, flags=re.S), main)
            self.manuscript_files.append(main)
            if not re.sub(r"<!--.*?-->", "", contents, flags=re.S).strip():
                self.unresolved("empty_manuscript", "Manuscript has no content")
            return
        visited, bib_files, texts = set(), set(), []

        def visit(path):
            if path in visited:
                return
            visited.add(path)
            self.manuscript_files.append(path)
            text = strip_tex_comments(self.read_text(path))
            texts.append(text)
            self.placeholders(text, path)
            for match in re.finditer(r"\\(?:input|include|subfile)\s*(?:\{([^}]+)\}|([^\s{}\\]+))", text):
                target = self.tex_target((match.group(1) or match.group(2)).strip(), main.parent, ".tex", f"{path.relative_to(self.root)} include")
                if target:
                    visit(target)
            for match in re.finditer(r"\\(?:bibliography|addbibresource)(?:\s*\[[^\]]*\])?\s*\{([^}]+)\}", text):
                for name in match.group(1).split(","):
                    target = self.tex_target(name.strip(), main.parent, ".bib", f"{path.relative_to(self.root)} bibliography")
                    if target:
                        bib_files.add(target)

        visit(main)
        for path in sorted(bib_files):
            for match in re.finditer(r"@([A-Za-z]+)\s*[{(]\s*([^,\s]+)\s*,", strip_tex_comments(self.read_text(path))):
                if match.group(1).lower() in ("comment", "preamble", "string"):
                    continue
                key = match.group(2)
                if key in self.bib_keys:
                    self.add("error", "duplicate_bib_key", f"Duplicate bibliography key: {key}")
                self.bib_keys.add(key)
        combined = "\n".join(texts)
        for key in re.findall(r"\\bibitem(?:\s*\[[^\]]*\])?\s*\{([^}]+)\}", combined):
            if key in self.bib_keys:
                self.add("error", "duplicate_bib_key", f"Duplicate bibliography key: {key}")
            self.bib_keys.add(key)
        labels = re.findall(r"\\label\s*\{([^}]+)\}", combined)
        seen = set()
        for label in labels:
            if label in seen:
                self.unresolved("duplicate_label", f"Duplicate TeX label: {label}")
            seen.add(label)
        for match in re.finditer(r"\\(?:ref|eqref|pageref|autoref|[cC]ref|[cC]pageref)\*?\s*\{([^}]+)\}", combined):
            for label in match.group(1).split(","):
                if label.strip() not in seen:
                    self.unresolved("undefined_reference", f"Undefined TeX reference: {label.strip()}")
        for match in re.finditer(r"\\(?:[cC]ite\w*|nocite|[pP]arencite|[tT]extcite|[aA]utocite)\*?(?:\s*\[[^\]]*\])*\s*\{([^}]+)\}", combined):
            for key in match.group(1).split(","):
                if key.strip() != "*" and key.strip() not in self.bib_keys:
                    self.unresolved("undefined_citation", f"Citation key absent from bibliography: {key.strip()}")

    def run(self):
        main = self.check_config()
        self.check_evidence()
        self.check_manuscript(main)
        return self.result()

    def result(self):
        return {"project": str(self.root), "mode": self.mode,
                "ok": not any(i["level"] == "error" for i in self.issues),
                "issues": self.issues,
                "scope": "Declared structure only; mathematical validity, novelty, source entailment, and hypothesis labeling require review."}


def is_external_locator(value):
    try:
        parsed = urlparse(value)
    except ValueError:
        return False
    return (parsed.scheme in ("http", "https") and bool(parsed.netloc)) or bool(re.match(r"^(?:doi:\s*)?10\.\d{4,9}/\S+$", value, re.I))


def strip_tex_comments(text):
    lines = []
    for line in text.splitlines():
        # Percent is escaped only by an odd number of immediately preceding slashes.
        end = len(line)
        for match in re.finditer("%", line):
            index, slashes = match.start() - 1, 0
            while index >= 0 and line[index] == "\\":
                slashes += 1
                index -= 1
            if slashes % 2 == 0:
                end = match.start()
                break
        lines.append(line[:end])
    result = "\n".join(lines)
    return re.sub(r"\\begin\{(verbatim\*?|lstlisting|minted)\}.*?\\end\{\1\}", "", result, flags=re.S)


def resolve_project(path):
    """Accept a project root or its configured paper directory (legacy usage)."""
    root = Path(path).resolve()
    if (root / "project.json").is_file():
        return root
    parent_config = root.parent / "project.json"
    if parent_config.is_file():
        try:
            config = json.loads(parent_config.read_text(encoding="utf-8"))
            main = config["manuscript"]["main"]
            if isinstance(main, str) and (root.parent / main).resolve().parent == root:
                return root.parent
        except (OSError, UnicodeError, ValueError, KeyError, TypeError):
            pass
    return root


def print_result(result):
    for issue in result["issues"]:
        print(f"{issue['level'].upper()} [{issue['code']}]: {issue['message']}")
    print(f"{result['mode'].capitalize()} structural check: {'passed' if result['ok'] else 'failed'}.")
    print(result["scope"])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("--mode", choices=("draft", "submission"), default="draft")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    root = resolve_project(args.project_dir)
    checker = Checker(root, args.mode)
    if not (root / "project.json").is_file():
        checker.add("error", "missing_project", "project.json is missing. For an older paper-only project, initialize a new project and copy its manuscript into the configured paper directory; existing papers are not automatically overwritten.")
        result = checker.result()
    else:
        result = checker.run()
    if args.as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_result(result)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
