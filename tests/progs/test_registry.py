import logging

from rom24.progs import registry


def test_register_and_resolve():
    calls = []

    @registry.register("mob", "greet_prog", "greet_prog_testling")
    def greet_prog_testling(mob, ch):
        calls.append((mob, ch))

    progs = registry.resolve("mob", [("greet_prog", "greet_prog_testling")])
    assert list(progs) == ["greet_prog"]
    progs["greet_prog"][0]("MOB", "CH")
    assert calls == [("MOB", "CH")]


def test_unknown_prog_warns_once(caplog):
    with caplog.at_level(logging.WARNING, logger="rom24.progs.registry"):
        registry.resolve("mob", [("fight_prog", "no_such_prog")])
        registry.resolve("mob", [("fight_prog", "no_such_prog")])
    warnings = [r for r in caplog.records if "no_such_prog" in r.message]
    assert len(warnings) == 1
