"""Command dispatch behavior (the front door: interpret -> cmd_table -> ctx)."""
from helpers import make_pc, run


def test_unknown_command_says_huh(booted_world):
    pc = make_pc()
    out = run(pc, "notarealcommandxyz")
    assert "Huh?" in out, "unknown command produced no Huh?: %r" % out


def test_known_command_dispatches(booted_world):
    pc = make_pc()
    out = run(pc, "score")
    assert "Str:" in out or "hit" in out.lower(), "score produced no output: %r" % out
