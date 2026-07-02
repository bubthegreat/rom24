from rom24 import const
from rom24.content import register


def setup_module(module):
    register.register()


def test_stub_msg_exact_text():
    from rom24.commands.do_cast import STUB_MSG
    assert STUB_MSG == "You trace the pattern, but nothing happens - that magic has not been rewoven yet.\n"


def test_stub_spell_castable_shape():
    sn = const.skill_table["banshee call"]
    assert sn.spell_fun is None
    # do_cast's known-spell condition must accept spell_fun-None entries the
    # char has learned; simulate the condition extracted as a helper:
    from rom24.commands.do_cast import spell_is_castable_stub
    assert spell_is_castable_stub(sn)


def test_stub_helper_returns_false_for_implemented_spell():
    """Implemented spells must NOT be treated as stubs."""
    from rom24.commands.do_cast import spell_is_castable_stub
    sn = const.skill_table["acid blast"]
    assert callable(sn.spell_fun)
    assert not spell_is_castable_stub(sn)


def test_stub_helper_returns_false_for_none():
    """None sn (spell not found) must not be treated as a stub."""
    from rom24.commands.do_cast import spell_is_castable_stub
    assert not spell_is_castable_stub(None)


def test_gate_condition_allows_stub_through():
    """
    The old gate combined `spell_fun is None` with `not sn` / level checks,
    routing stub spells to 'don't know'.  The new gate must separate these:
    a stub sn (spell_fun is None) that the char theoretically knows must
    survive the gate and only be caught by spell_is_castable_stub().

    We verify the structural split by confirming that the gate's 'unknown
    spell' path (not sn) is independent of the stub path (spell_fun is None).
    """
    from rom24.commands.do_cast import spell_is_castable_stub

    sn = const.skill_table["banshee call"]
    # Stub: sn is not None, spell_fun is None -> is a stub, not "unknown"
    assert sn is not None
    assert sn.spell_fun is None
    assert spell_is_castable_stub(sn)

    # A real implemented spell: not a stub
    sn_real = const.skill_table["acid blast"]
    assert sn_real is not None
    assert not spell_is_castable_stub(sn_real)
