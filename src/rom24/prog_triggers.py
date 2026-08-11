"""Area program (prog) trigger registry.

Progs are ordinary Python functions bundled with an area (``areas/<x>/progs.py``)
that react to game events. They register via decorators keyed to a mob or room
vnum and receive a curated :class:`~rom24.prog_context.Ctx` handle — the only
world surface a prog is given (the guardrail). A prog that raises is caught and
logged; it never crashes the tick.

v1 triggers: speech (a mob hears a keyword), greet (a char enters a mob's room),
entry (a char enters a room). More can be added by registering a dict + a
``fire_*`` helper and wiring one emit point.
"""
import logging

from rom24.prog_context import Ctx

logger = logging.getLogger(__name__)

_speech = {}  # mob_vnum -> [(keyword_or_None, func)]
_greet = {}   # mob_vnum -> [func]
_entry = {}   # room_vnum -> [func]


def on_speech(mob, keyword=None):
    """Fire when someone speaks in the mob's room (optionally matching a keyword)."""

    def deco(func):
        _speech.setdefault(mob, []).append((keyword.lower() if keyword else None, func))
        return func

    return deco


def on_greet(mob):
    """Fire when a character enters the mob's room."""

    def deco(func):
        _greet.setdefault(mob, []).append(func)
        return func

    return deco


def on_entry(room):
    """Fire when a character enters the room."""

    def deco(func):
        _entry.setdefault(room, []).append(func)
        return func

    return deco


def clear():
    """Drop all registered progs (called before (re)loading areas)."""
    _speech.clear()
    _greet.clear()
    _entry.clear()


def _run(func, ctx):
    try:
        func(ctx)
    except Exception:  # a bad prog must never crash the game loop
        logger.exception("Prog error in %s", getattr(func, "__name__", "?"))


def fire_speech(mob, actor, argument, room):
    low = (argument or "").lower()
    for keyword, func in _speech.get(mob.vnum, []):
        if keyword is None or keyword in low:
            _run(func, Ctx(mob=mob, actor=actor, arg=argument, room=room))


def fire_greet(mob, actor, room):
    for func in _greet.get(mob.vnum, []):
        _run(func, Ctx(mob=mob, actor=actor, arg="", room=room))


def fire_entry(room, actor):
    for func in _entry.get(room.vnum, []):
        _run(func, Ctx(mob=None, actor=actor, arg="", room=room))
