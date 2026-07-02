import os
import pathlib
import subprocess
import sys

import pytest

KBK = pathlib.Path(os.path.expanduser("~/Development/kbk"))
REPO = pathlib.Path(__file__).resolve().parents[2]

pytestmark = pytest.mark.skipif(not KBK.exists(), reason="kbk checkout not present")


def run_import(dest):
    subprocess.run(
        [sys.executable, "-m", "tools.kbk_import", "--kbk", str(KBK), "--repo", str(dest)],
        check=True, cwd=REPO, env={**os.environ, "PYTHONPATH": str(REPO)})


def test_full_conversion_counts(tmp_path):
    run_import(tmp_path)
    ns = {}
    exec((tmp_path / "src/rom24/content/classes.py").read_text(), ns)
    assert len(ns["CLASSES"]) == 13
    exec((tmp_path / "src/rom24/content/races.py").read_text(), ns)
    assert len(ns["PC_RACES"]) >= 20
    exec((tmp_path / "src/rom24/content/skills.py").read_text(), ns)
    assert len(ns["SKILLS"]) > 300
    exec((tmp_path / "src/rom24/content/groups.py").read_text(), ns)
    assert len(ns["GROUPS"]) >= 30
    assert len(list((tmp_path / "src/area/kbk").glob("*.are"))) == 100
    assert (tmp_path / "src/area/kbk/olc.hlp").exists()


def test_idempotent(tmp_path):
    run_import(tmp_path)
    first = {p: p.read_bytes() for p in (tmp_path / "src/rom24/content").iterdir()}
    run_import(tmp_path)
    assert first == {p: p.read_bytes() for p in (tmp_path / "src/rom24/content").iterdir()}
