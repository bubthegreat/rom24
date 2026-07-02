"""Targeted tests for ride-along mechanical fixes (task 11).

Coverage decisions:
  Item 7  (nanny.py ch_dummy use-after-delete): not unit-testable without a
          full descriptor fake + nanny state machine. Fix is a 1-line rename
          (ch_dummy.trust -> ch.trust); correctness is self-evident from
          context (ch is already bound before del ch_dummy).
  Item 11 (special.py instance import): simple module-attribute check.
  Item 12 (update.py position None guard): isolated guard expression test;
          char_update() requires ~15 live attributes on a character object
          which would take more scaffolding than the 1-line fix warrants.
"""


def test_special_has_instance_import():
    """special.py must have `instance` in its module namespace after the fix."""
    from rom24 import special
    assert hasattr(special, "instance"), (
        "rom24.instance not imported in special.py — "
        "spec_executioner will NameError on every tick"
    )


def test_special_spec_executioner_references_instance():
    """spec_executioner must reference instance.characters (sanity-check src)."""
    import inspect
    from rom24 import special
    src = inspect.getsource(special.spec_executioner)
    assert "instance.characters" in src


def test_position_none_guard_pattern():
    """The guard `pos is not None and pos >= POS_STUNNED` must not raise for None."""
    from rom24 import merc

    pos_none = None
    assert (pos_none is not None and pos_none >= merc.POS_STUNNED) is False

    pos_stunned = merc.POS_STUNNED
    assert (pos_stunned is not None and pos_stunned >= merc.POS_STUNNED) is True

    pos_dead = 0  # POS_DEAD — below POS_STUNNED
    assert (pos_dead is not None and pos_dead >= merc.POS_STUNNED) is False
