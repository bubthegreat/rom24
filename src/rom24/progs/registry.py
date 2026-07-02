"""Prog registry: name -> function per kind, resolved onto instances at creation.

KBK's #IMPROGS bindings (loaded as (progtype, progname) tuples on templates since
Phase 1) resolve here. Unknown prognames warn once and stay inert.
"""
import logging

logger = logging.getLogger(__name__)

PROG_KINDS = ("mob", "item", "room")
_registry: dict = {kind: {} for kind in PROG_KINDS}
_warned: set = set()


def register(kind, trigger, name):
    if kind not in PROG_KINDS:
        raise ValueError(f"Unknown prog kind {kind!r}; expected one of {PROG_KINDS}")
    def deco(fn):
        _registry[kind][name] = (trigger, fn)
        return fn
    return deco


def resolve(kind, bindings):
    progs: dict = {}
    for progtype, progname in bindings:
        entry = _registry[kind].get(progname)
        if entry is None:
            if (kind, progname) not in _warned:
                _warned.add((kind, progname))
                logger.warning("prog %s/%s not implemented; binding inert", kind, progname)
            continue
        trigger, fn = entry
        if trigger != progtype:
            logger.warning("prog %s bound as %s but registered as %s; using registration",
                           progname, progtype, trigger)
        progs.setdefault(trigger, []).append(fn)
    return progs
