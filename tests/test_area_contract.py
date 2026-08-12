"""Area contract: any area that ships behavior (progs) must ship tests.

Self-contained area folders can add real Python progs (mob speech, greet, give,
death, random handlers) and, later, area commands. Those are game logic. This
test enforces that such an area also carries its own tests under
``src/areas/<name>/tests/`` so the behavior is proven, not just present — the
same way Midgaard's wizard progs are covered by test_wizard_progs.py.

An area with no progs is exempt (nothing to prove yet).
"""
import glob
import os
import re

AREAS_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "areas")

# A prog is registered by one of the prog decorators in progs.py.
_PROG_MARKER = re.compile(r"@on_(speech|greet|give|death|random|entry)\b")


def _areas_with_progs():
    """Yield (area_name, progs_path) for every area whose progs.py registers a prog."""
    for progs_path in sorted(glob.glob(os.path.join(AREAS_DIR, "*", "progs.py"))):
        with open(progs_path) as fp:
            if _PROG_MARKER.search(fp.read()):
                yield os.path.basename(os.path.dirname(progs_path)), progs_path


def test_areas_with_progs_have_tests():
    """Every area that registers progs must have at least one test file."""
    offenders = []
    for area, progs_path in _areas_with_progs():
        test_glob = os.path.join(os.path.dirname(progs_path), "tests", "test_*.py")
        if not glob.glob(test_glob):
            offenders.append(area)
    assert not offenders, (
        "these areas ship progs but no tests (add src/areas/<name>/tests/test_*.py):\n"
        + "\n".join(sorted(offenders))
    )


def test_contract_actually_sees_a_prog_area():
    """Guard the guard: if this finds nothing, the marker/glob has drifted."""
    assert list(_areas_with_progs()), "no prog areas discovered — contract check is inert"
