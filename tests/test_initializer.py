"""Safety and behavior tests for configurable project initialization."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "init_ieee_project.py"
SPEC = importlib.util.spec_from_file_location("initializer", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class InitializerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.project = self.base / "research project with spaces"

    def run_init(self, *options, expected=0, path=None):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(path or self.project), *options],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def config(self):
        return json.loads((self.project / "project.json").read_text())

    def test_backward_compatible_defaults_and_no_fabricated_results(self):
        self.run_init("--title", "Control & Estimation", "--direction", "observer design", "--author", "A_Researcher")
        config = self.config()
        self.assertEqual(config["manuscript"], {"format": "ieee", "main": "paper/main.tex"})
        self.assertEqual(config["experiment"]["engine"], "matlab")
        self.assertEqual(config["direction"], "observer design")
        self.assertEqual((self.project / "paper/references.bib").read_text(), "")
        self.assertEqual(json.loads((self.project / "evidence.json").read_text())["claims"], [])
        self.assertEqual(list((self.project / "experiments/raw").iterdir()), [])
        self.assertIn("sci_writing:NotConfigured", (self.project / "experiments/run_experiments.m").read_text())

    def test_all_formats_and_engines(self):
        for form in ("ieee", "article", "markdown"):
            for engine in ("matlab", "python", "none"):
                with self.subTest(form=form, engine=engine):
                    path = self.base / f"{form}-{engine}"
                    self.run_init("--format", form, "--engine", engine, path=path)
                    config = json.loads((path / "project.json").read_text())
                    self.assertTrue((path / config["manuscript"]["main"]).is_file())
                    entrypoint = config["experiment"]["entrypoint"]
                    self.assertEqual(entrypoint is None, engine == "none")
                    if entrypoint:
                        self.assertTrue((path / entrypoint).is_file())
                    self.assertEqual((path / "paper/main.tex").exists(), form != "markdown")

    def test_python_engine_refuses_to_fabricate_results(self):
        self.run_init("--engine", "python")
        result = subprocess.run([sys.executable, str(self.project / "experiments/run_experiments.py")], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not configured", result.stderr.lower())
        self.assertEqual(list((self.project / "experiments/raw").iterdir()), [])

    def test_rerun_preserves_edits_and_existing_choices(self):
        self.run_init("--format", "markdown", "--engine", "none", "--title", "Custom title")
        manuscript = self.project / "paper/manuscript.md"
        manuscript.write_text("My research edits\n")
        config_bytes = (self.project / "project.json").read_bytes()
        (self.project / "notes/paper-cards.md").unlink()
        result = self.run_init()
        self.assertIn("existing files preserved", result.stdout)
        self.assertEqual(manuscript.read_text(), "My research edits\n")
        self.assertEqual((self.project / "project.json").read_bytes(), config_bytes)
        self.assertTrue((self.project / "notes/paper-cards.md").is_file())
        self.assertFalse((self.project / "paper/main.tex").exists())
        self.run_init("--format", "article", expected=2)
        self.assertFalse((self.project / "paper/main.tex").exists())

    def test_force_backs_up_all_replaced_files_without_collisions(self):
        self.run_init("--format", "article", "--engine", "python")
        files = {str(path.relative_to(self.project)): path.read_bytes() for path in self.project.rglob("*") if path.is_file()}
        manuscript = self.project / "paper/main.tex"
        manuscript.write_text("edited manuscript\n")
        files["paper/main.tex"] = manuscript.read_bytes()
        self.run_init("--force", "--title", "Changed title")
        first = list((self.project / ".sci-writing-backups").iterdir())
        self.assertEqual(len(first), 1)
        for name, contents in files.items():
            self.assertEqual((first[0] / name).read_bytes(), contents, name)
        self.assertIn("Changed title", manuscript.read_text())
        self.run_init("--force")
        self.assertEqual(len(list((self.project / ".sci-writing-backups").iterdir())), 2)

    def make_symlink(self, source, target, is_directory=False):
        try:
            target.symlink_to(source, target_is_directory=is_directory)
        except (OSError, NotImplementedError):
            self.skipTest("Creating symlinks is not supported on this platform")

    def test_symlink_parent_and_project_root_rejected(self):
        outside = self.base / "outside"
        outside.mkdir()
        self.make_symlink(outside, self.project, True)
        self.run_init(expected=2)
        self.assertEqual(list(outside.iterdir()), [])

    def test_symlink_managed_directory_rejected_before_any_writes(self):
        self.project.mkdir()
        outside = self.base / "outside"
        outside.mkdir()
        self.make_symlink(outside, self.project / "paper", True)
        self.run_init("--force", expected=2)
        self.assertFalse((self.project / "project.json").exists())
        self.assertEqual(list(outside.iterdir()), [])

    def test_dangling_symlink_and_backup_symlink_rejected(self):
        self.project.mkdir()
        self.make_symlink(self.base / "missing", self.project / "project.json")
        self.run_init(expected=2)
        (self.project / "project.json").unlink()
        self.make_symlink(self.base / "missing", self.project / ".sci-writing-backups", True)
        self.run_init("--force", expected=2)
        self.assertFalse((self.project / "project.json").exists())

    def test_wrong_path_type_rejected_before_writes(self):
        (self.project / "paper/main.tex").mkdir(parents=True)
        self.run_init(expected=2)
        self.assertFalse((self.project / "project.json").exists())

    def test_latex_escaping_is_not_recursive(self):
        title = "CBF & USV_50% #1 $x$ {A} ~ ^ \\"
        self.run_init("--title", title, "--author", "A&B")
        text = (self.project / "paper/main.tex").read_text()
        self.assertIn(r"\title{CBF \& USV\_50\% \#1 \$x\$ \{A\} \textasciitilde{} \textasciicircum{} \textbackslash{}}", text)
        self.assertIn(r"\author{A\&B}", text)
        self.assertEqual(self.config()["title"], title)

    def test_empty_title_and_path_escape_rejected(self):
        self.run_init("--title", " ", expected=2)
        self.assertFalse(self.project.exists())
        with self.assertRaises(ValueError):
            MODULE.safe_target(self.project, "../outside.txt")
        with self.assertRaises(ValueError):
            MODULE.safe_target(self.project, str(self.base / "outside.txt"))


if __name__ == "__main__":
    unittest.main()
