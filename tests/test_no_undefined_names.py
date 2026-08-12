"""Static guard: no undefined names in shipped command/spell/prog code.

Undefined names (e.g. a spell body using ``instance`` without importing it, or a
stray ``obj``) are latent NameErrors that only fire when the command/spell runs,
so they slip past import and most tests. pyflakes catches them statically. This
test fails until every such bug is fixed — the same class the ctx-conversion
surfaced.
"""
import glob
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_DIRS = [
    "src/packs/core/commands",
    "src/packs/core/spells",
]


def _pack_files():
    files = []
    for d in TARGET_DIRS:
        files.extend(glob.glob(os.path.join(ROOT, d, "*.py")))
    return sorted(f for f in files if not os.path.basename(f).startswith("__"))


def test_no_undefined_names_in_pack_code():
    files = _pack_files()
    assert files, "no pack files found"
    result = subprocess.run(
        [sys.executable, "-m", "pyflakes", *files],
        capture_output=True,
        text=True,
    )
    undefined = [
        line for line in result.stdout.splitlines() if "undefined name" in line
    ]
    assert not undefined, "undefined names (latent NameErrors) found:\n" + "\n".join(
        line.replace(ROOT + "/", "") for line in undefined
    )
