"""Prog dispatch honoring C veto semantics (see research doc trigger table).

KBK area census: no (vnum, progtype) pairs are bound twice to a single vnum;
the list form is defensive against future bindings.

Run-all semantics: all progs for a trigger fire even after a veto is
recorded. C data has at most one prog per (vnum, trigger); run-all is
forward-compatible if that ever changes, and is safer than stop-at-veto
for side-effect progs (announce/save/etc.) that must run regardless.
"""
import logging

logger = logging.getLogger(__name__)

VETO_ON_TRUE = {"death_prog", "sac_prog", "give_prog"}
VETO_ON_FALSE = {"move_prog"}


def fire(target, trigger, *args):
    """Fire all progs registered for a trigger.

    Args:
        target: Object with optional `.progs` dict (trigger -> [callables]).
        trigger: Trigger name.
        *args: Arguments to pass to each prog callable.

    Returns:
        bool: True iff ANY prog returned a veto value for a veto-capable trigger.
              - VETO_ON_TRUE triggers: veto if any prog returns True.
              - VETO_ON_FALSE triggers: veto if any prog returns False.
              - Non-veto triggers: always return False.
    """
    progs = getattr(target, "progs", None)
    if not progs or trigger not in progs:
        return False
    veto = False
    for fn in progs[trigger]:
        try:
            result = fn(target, *args)
        except Exception:
            logger.exception("prog %s on %r failed", getattr(fn, "__name__", fn), target)
            continue
        if trigger in VETO_ON_TRUE and result is True:
            veto = True
        elif trigger in VETO_ON_FALSE and result is False:
            veto = True
    return veto
