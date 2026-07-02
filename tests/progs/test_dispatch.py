"""Test prog dispatch with C veto semantics."""
from typing import Any, Dict, List

from rom24.progs import dispatch


class T:
    progs: Dict[str, List[Any]]


def _target(trigger, *fns):
    t = T()
    t.progs = {trigger: list(fns)}
    return t


def test_fire_no_progs_returns_false():
    assert dispatch.fire(T(), "greet_prog", "ch") is False


def test_void_trigger_runs_all_and_returns_false():
    seen = []
    t = _target("greet_prog", lambda a: seen.append(("one", a)), lambda a: seen.append(("two", a)))
    assert dispatch.fire(t, "greet_prog", "ch") is False
    assert seen == [("one", "ch"), ("two", "ch")]


def test_death_prog_true_vetoes():
    t = _target("death_prog", lambda killer: True)
    assert dispatch.fire(t, "death_prog", "killer") is True


def test_move_prog_false_vetoes():
    t = _target("move_prog", lambda ch, room, door: False)
    assert dispatch.fire(t, "move_prog", "ch", "room", 0) is True


def test_prog_exception_is_contained(caplog):
    import logging
    def boom(ch):
        raise RuntimeError("prog bug")
    t = _target("greet_prog", boom)
    with caplog.at_level(logging.ERROR, logger="rom24.progs.dispatch"):
        assert dispatch.fire(t, "greet_prog", "ch") is False
    assert any("prog bug" in r.message or "boom" in r.message for r in caplog.records)


def test_move_prog_exception_does_not_veto(caplog):
    import logging
    def boom(ch, room, door):
        raise RuntimeError("move bug")
    t = _target("move_prog", boom)
    with caplog.at_level(logging.ERROR, logger="rom24.progs.dispatch"):
        assert dispatch.fire(t, "move_prog", "ch", "room", 0) is False


def test_move_prog_none_return_does_not_veto():
    # Python default return (None) must not be treated as False for veto purposes.
    t = _target("move_prog", lambda ch, room, door: None)
    assert dispatch.fire(t, "move_prog", "ch", "room", 0) is False
