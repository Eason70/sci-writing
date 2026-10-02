"""Regression checks for evidence integrity and real versus nominal builds."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from check_project import Checker, resolve_project  # noqa: E402
import build_paper  # noqa: E402


class ProjectTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="sci validation ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "project with spaces"
        (self.root / "paper" / "sections").mkdir(parents=True)
        (self.root / "notes").mkdir()
        self.config = {
            "schema_version": 1, "title": "A control paper", "direction": "", "author": "",
            "manuscript": {"format": "article", "main": "paper/main.tex"},
            "experiment": {"engine": "none", "entrypoint": None, "status": "not_configured", "seed": 0},
            "research": {"time_domain": "", "dynamics": [], "objectives": [], "constraints": [], "contribution_type": ""},
        }
        self.evidence = {"schema_version": 1, "sources": [], "claims": [], "runs": []}
        self.write_json()
        (self.root / "paper/main.tex").write_text(
            "\\documentclass{article}\n\\begin{document}\nA manuscript.\n\\end{document}\n", encoding="utf-8")

    def write_json(self):
        for name, value in (("project.json", self.config), ("evidence.json", self.evidence)):
            (self.root / name).write_text(json.dumps(value), encoding="utf-8")

    def result(self, mode="draft"):
        self.write_json()
        return Checker(self.root, mode).run()

    def codes(self, result):
        return {i["code"] for i in result["issues"]}

    def add_claim(self, **overrides):
        claim = {"id": "claim-1", "text": "The stated local bound holds.", "kind": "theory",
                 "status": "supported", "in_manuscript": True, "assumptions": ["A1"],
                 "limitations": [], "evidence": [{"evidence_id": "source-1", "locator": "Lemma 1, lines 3-9"}]}
        claim.update(overrides)
        self.evidence["claims"].append(claim)
        return claim

    def add_source(self, **overrides):
        (self.root / "notes/proof.md").write_text("A derivation.", encoding="utf-8")
        source = {"id": "source-1", "type": "derivation", "title": "Derivation", "locator": "notes/proof.md", "verification": "content_checked"}
        source.update(overrides)
        self.evidence["sources"].append(source)
        return source

    def completed_run(self):
        for path in ("notes/config.json", "notes/environment.txt", "notes/raw.csv"):
            (self.root / path).write_text("recorded data", encoding="utf-8")
        run = {"id": "run-1", "status": "completed", "config_path": "notes/config.json", "environment_path": "notes/environment.txt",
               "code_revision": "sha256:recorded-code-content", "seed": 17, "raw_data": ["notes/raw.csv"], "figures": []}
        self.evidence["runs"].append(run)
        return run

    def test_minimal_project_does_not_require_all_research_routes(self):
        self.assertTrue(self.result("submission")["ok"])

    def test_valid_local_support_and_unused_unverified_literature(self):
        self.add_source()
        self.add_source(id="background-1", type="literature", locator="https://example.org/paper", verification="unverified")
        self.add_claim()
        self.assertTrue(self.result("submission")["ok"])

    def test_draft_gap_warning_becomes_submission_error(self):
        self.add_claim(status="needs_review", evidence=[])
        result = self.result()
        self.assertTrue(result["ok"])
        self.assertIn("unsupported_claim", self.codes(result))
        self.assertFalse(self.result("submission")["ok"])

    def test_supported_claim_requires_content_not_just_metadata(self):
        self.add_source(verification="metadata_verified")
        self.add_claim()
        result = self.result()
        self.assertFalse(result["ok"])
        self.assertIn("unverified_support", self.codes(result))

    def test_missing_and_duplicate_evidence_ids(self):
        self.add_claim()
        self.assertIn("missing_evidence", self.codes(self.result()))
        self.add_source()
        self.add_source()
        self.assertIn("duplicate_id", self.codes(self.result()))

    def test_malformed_shapes_report_errors_without_traceback(self):
        self.config["research"] = []
        self.config["experiment"]["seed"] = True
        self.evidence["sources"] = [None, {"id": [], "type": {}}]
        self.evidence["runs"] = ["bad"]
        self.evidence["claims"] = [{"id": {}, "evidence": [None]}]
        result = self.result()
        self.assertFalse(result["ok"])
        self.assertIn("schema", self.codes(result))

    def test_invalid_json_machine_readable_cli(self):
        (self.root / "project.json").write_text("{", encoding="utf-8")
        proc = subprocess.run([sys.executable, str(SCRIPTS / "check_project.py"), str(self.root), "--json"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("invalid_json", self.codes(json.loads(proc.stdout)))
        self.assertNotIn("Traceback", proc.stderr)

    def test_external_paths_and_symlink_escape_rejected(self):
        for locator in ("../../outside.md", "C:\\outside.md", "/tmp/outside.md", "..\\..\\outside.md"):
            with self.subTest(locator=locator):
                self.evidence["sources"] = []
                self.add_source(locator=locator)
                self.assertIn("path_escape", self.codes(self.result()))
        outside = Path(self.temp.name) / "outside.md"
        outside.write_text("outside", encoding="utf-8")
        link = self.root / "notes/link.md"
        try:
            link.symlink_to(outside)
        except OSError:
            return
        self.evidence["sources"] = []
        self.add_source(locator="notes/link.md")
        self.assertIn("path_escape", self.codes(self.result()))

    def test_completed_run_requires_actual_raw_data_and_records(self):
        run = self.completed_run()
        self.add_claim(kind="empirical", evidence=[{"evidence_id": "run-1", "locator": "raw.csv column error, rows 1-50"}])
        self.assertTrue(self.result("submission")["ok"])
        (self.root / "notes/raw.csv").unlink()
        self.assertIn("missing_file", self.codes(self.result()))
        run["raw_data"] = []
        run["code_revision"] = ""
        run["seed"] = None
        codes = self.codes(self.result())
        self.assertIn("run_incomplete", codes)
        self.assertIn("schema", codes)

    def test_incomplete_runs_allowed_but_cannot_support_claims(self):
        self.evidence["runs"].append({"id": "run-1", "status": "failed", "config_path": "", "environment_path": "", "code_revision": "", "seed": None, "raw_data": [], "figures": []})
        self.assertTrue(self.result()["ok"])
        self.add_claim(evidence=[{"evidence_id": "run-1", "locator": "attempt log"}])
        self.assertIn("unverified_support", self.codes(self.result()))

    def test_hypothesis_label_status_consistency(self):
        self.add_claim(kind="hypothesis", status="hypothesis", evidence=[])
        self.assertTrue(self.result("submission")["ok"])
        self.evidence["claims"][0]["status"] = "supported"
        self.assertIn("claim_status", self.codes(self.result()))

    def test_included_tex_checked_comments_ignored(self):
        (self.root / "paper/main.tex").write_text(
            r"\documentclass{article}" + "\n" + r"% TODO \cite{ignored} \ref{ignored}" + "\n" +
            r"\begin{document}\input{sections/result}\bibliography{references}\end{document}", encoding="utf-8")
        (self.root / "paper/sections/result.tex").write_text(r"TODO: result. \citep[see][p. 3]{missing} \eqref{missing-eq}", encoding="utf-8")
        (self.root / "paper/references.bib").write_text("", encoding="utf-8")
        result = self.result()
        self.assertTrue(result["ok"])
        self.assertEqual(self.codes(result), {"placeholder", "undefined_citation", "undefined_reference"})
        self.assertFalse(self.result("submission")["ok"])
        self.assertFalse(any("ignored" in issue["message"] for issue in result["issues"]))

    def test_resolved_tex_refs_cites_and_commented_todo(self):
        (self.root / "paper/main.tex").write_text(r"\documentclass{article}\begin{document}\label{eq:one}\eqref{eq:one}\cite{key}\bibliography{references}\end{document}" + "\n% TODO example", encoding="utf-8")
        (self.root / "paper/references.bib").write_text('@article{key, title={A record}, author={A}, year={2020}}', encoding="utf-8")
        self.assertTrue(self.result("submission")["ok"])

    def test_inline_bibliography_supports_optional_labels(self):
        (self.root / "paper/main.tex").write_text(r"\documentclass{article}\begin{document}\cite{key}\begin{thebibliography}{9}\bibitem[Author, 2020]{key} A record.\end{thebibliography}\end{document}", encoding="utf-8")
        self.assertTrue(self.result("submission")["ok"])

    def test_old_paper_path_resolves_only_configured_parent(self):
        self.assertEqual(resolve_project(self.root / "paper"), self.root)
        (self.root / "unrelated").mkdir()
        self.assertEqual(resolve_project(self.root / "unrelated"), self.root / "unrelated")

    def test_markdown_reports_no_pdf_and_no_latex_dependency(self):
        self.config["manuscript"] = {"format": "markdown", "main": "paper/manuscript.md"}
        (self.root / "paper/manuscript.md").write_text("# A paper\nA paragraph.", encoding="utf-8")
        self.write_json()
        with mock.patch.object(build_paper.shutil, "which", side_effect=AssertionError("should not need TeX")), contextlib.redirect_stdout(io.StringIO()) as output:
            code = build_paper.build(self.root, "submission")
        self.assertEqual(code, 0)
        self.assertIn("No PDF was built", output.getvalue())
        self.assertFalse((self.root / "paper/build").exists())

    def mock_latex(self, final_log, stdout="", code=0):
        def run(*args, **kwargs):
            self.assertFalse(kwargs.get("shell", False))
            self.assertIn("-no-shell-escape", args[0])
            target = self.root / "paper/build"
            (target / "main.log").write_text(final_log, encoding="utf-8")
            (target / "main.pdf").write_bytes(b"%PDF-mock")
            return subprocess.CompletedProcess(args[0], code, stdout=stdout)
        return run

    def test_submission_rejects_final_log_warnings_despite_exit_zero(self):
        with mock.patch.object(build_paper.shutil, "which", return_value="/mock/latexmk"), mock.patch.object(build_paper.subprocess, "run", side_effect=self.mock_latex("LaTeX Warning: There were undefined references.")), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(build_paper.build(self.root, "submission"), 1)
            self.assertEqual(build_paper.build(self.root, "draft"), 0)

    def test_transient_rerun_warning_does_not_override_clean_final_log(self):
        with mock.patch.object(build_paper.shutil, "which", return_value="/mock/latexmk"), mock.patch.object(build_paper.subprocess, "run", side_effect=self.mock_latex("Output written on main.pdf", "LaTeX Warning: There were undefined references.")), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(build_paper.build(self.root, "submission"), 0)

    def test_ieee_class_missing_gives_actionable_diagnostic(self):
        message = build_paper.dependency_message("! LaTeX Error: File `IEEEtran.cls' not found.")
        self.assertIn("Install the IEEEtran package", message)

    @unittest.skipUnless(shutil.which("latexmk") and shutil.which("pdflatex"), "TeX toolchain is unavailable")
    def test_real_article_build_in_path_with_spaces_and_legacy_argument(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            code = build_paper.build(self.root / "paper", "submission")
        self.assertEqual(code, 0, output.getvalue())
        self.assertTrue((self.root / "paper/build/main.pdf").is_file())


if __name__ == "__main__":
    unittest.main()
