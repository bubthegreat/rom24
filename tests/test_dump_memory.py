"""Tests for the do_memory and do_dump immortal debug commands.

Boots the full world once, then verifies do_memory reports non-empty world
counts to the character and do_dump runs without raising.
"""
import os

import pytest




def _make_char(capture):
    """Build a live NPC and redirect its ``send`` into ``capture`` list."""
    from rom24 import instance, object_creator

    vnum = next(iter(instance.npc_templates))
    template = instance.npc_templates[vnum]
    ch = object_creator.create_mobile(template)
    ch.send = lambda pstr: capture.append(pstr)
    return ch


def test_do_memory_reports_counts(booted_world, command):

    captured = []
    ch = _make_char(captured)

    command('memory')(ch, "")

    output = "".join(captured)
    assert output, "do_memory sent no output"
    # World booted with a non-trivial number of mob prototypes.
    assert "Mobs" in output
    assert "Rooms" in output

    # At least one line reports a plausible (non-zero, multi-hundred) count.
    import re

    numbers = [int(n) for n in re.findall(r"\d+", output)]
    assert any(n > 100 for n in numbers), f"no plausible count in output: {output!r}"


def test_do_dump_runs(booted_world, tmp_path, monkeypatch, command):

    # Run in a temp cwd so the mem.dmp file lands somewhere disposable.
    monkeypatch.chdir(tmp_path)

    captured = []
    ch = _make_char(captured)

    # Must not raise.
    command('dump')(ch, "")

    assert "".join(captured).strip() == "Dumped."
    assert os.path.isfile(tmp_path / "mem.dmp")
    assert (tmp_path / "mem.dmp").read_text().strip(), "mem.dmp is empty"
