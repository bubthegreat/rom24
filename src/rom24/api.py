"""Stable ctx-style API for commands and spells (and, later, progs).

A command/spell file imports ONLY ``from rom24 import api``. Behavior goes
through a per-call ``ctx`` handle; registration and constants come from this
module. This is the curated, stable surface a content-pack author writes
against — engine internals can change behind it.

- ``@api.command(name, pos=..., level=..., aliases=(...))`` registers a
  ``def do_x(ctx): ...`` command.
- ``@api.spell(name, ...)`` registers a ``def spell_x(ctx): ...`` spell.
- ``api.POS_FIGHTING`` etc. re-export every ``merc`` constant; ``api.merc`` is
  the full module.
- ``ctx.engine`` is an explicit ESCAPE HATCH exposing raw engine modules for
  anything not yet wrapped. It is deliberately UNSTABLE; prefer ``ctx`` methods.
"""
import random

from rom24 import (
    merc,
    interp,
    fight,
    handler_game,
    state_checks,
    instance,
    const,
    game_utils,
    handler_magic,
    object_creator,
    handler_ch,
    handler_item,
    prog_triggers,
)

# Re-export every public merc constant onto this module (api.POS_FIGHTING, ...).
for _name in dir(merc):
    if not _name.startswith("_"):
        globals()[_name] = getattr(merc, _name)

# Spell slot helper (api.SLOT(n)).
SLOT = const.SLOT


class _Engine:
    """Raw engine modules. UNSTABLE escape hatch — prefer ctx.* methods."""

    merc = merc
    fight = fight
    handler_game = handler_game
    state_checks = state_checks
    instance = instance
    const = const
    game_utils = game_utils
    handler_magic = handler_magic
    object_creator = object_creator
    handler_ch = handler_ch
    handler_item = handler_item
    prog_triggers = prog_triggers


class BaseCtx:
    """Behavior shared by CommandCtx and SpellCtx."""

    def __init__(self, ch):
        self.ch = ch
        self.engine = _Engine

    @property
    def room(self):
        return self.ch.in_room

    @property
    def fighting(self):
        return self.ch.fighting

    # --- output ---
    def send(self, text):
        self.ch.send(text if text.endswith("\n") else text + "\n")

    def act(self, fmt, arg1=None, arg2=None, to=merc.TO_ROOM):
        handler_game.act(fmt, self.ch, arg1, arg2, to)

    def to_char(self, fmt, arg1=None, arg2=None):
        handler_game.act(fmt, self.ch, arg1, arg2, merc.TO_CHAR)

    def to_room(self, fmt, arg1=None, arg2=None):
        handler_game.act(fmt, self.ch, arg1, arg2, merc.TO_ROOM)

    # --- lookup ---
    def char_in_room(self, name):
        return self.ch.get_char_room(name)

    def char_world(self, name):
        return self.ch.get_char_world(name)

    def mob_proto(self, vnum):
        return instance.npc_templates.get(vnum)

    def obj_proto(self, vnum):
        return instance.item_templates.get(vnum)

    def room_at(self, vnum):
        ids = instance.instances_by_room.get(vnum)
        return instance.rooms[ids[0]] if ids else None

    # --- combat ---
    def damage(self, victim, amount, dt=merc.TYPE_UNDEFINED, dam_type=merc.DAM_NONE, show=True):
        return fight.damage(self.ch, victim, amount, dt, dam_type, show)

    def multi_hit(self, victim, dt=merc.TYPE_UNDEFINED):
        return fight.multi_hit(self.ch, victim, dt)

    def kill(self, victim):
        return fight.multi_hit(self.ch, victim, merc.TYPE_UNDEFINED)

    def is_safe(self, victim):
        return fight.is_safe(self.ch, victim)

    def check_killer(self, victim):
        return fight.check_killer(self.ch, victim)

    # --- skills ---
    def skill(self, name):
        return self.ch.get_skill(name)

    def improve(self, name, success, mult=1):
        if self.ch.is_pc:
            self.ch.check_improve(name, success, mult)

    def skill_beats(self, name):
        return const.skill_table[name].beats

    def skill_level(self, name):
        return const.skill_table[name].skill_level[self.ch.guild.name]

    def cast(self, spell_name, target=None):
        sk = const.skill_table.get(spell_name)
        if sk and getattr(sk, "spell_fun", None):
            sk.spell_fun(spell_name, self.ch.level, self.ch, target or self.ch, merc.TARGET_CHAR)

    # --- timing ---
    def wait(self, beats):
        state_checks.WAIT_STATE(self.ch, beats)

    def daze(self, victim, beats):
        state_checks.DAZE_STATE(victim, beats)

    # --- rng ---
    def rand(self, low, high):
        return random.randint(low, high)

    def dice(self, number, size):
        return game_utils.dice(number, size)


class CommandCtx(BaseCtx):
    def __init__(self, ch, argument):
        super().__init__(ch)
        self.arg = argument or ""

    def word(self):
        """Pop and return the next word of the argument (mutates ctx.arg)."""
        rest, word = game_utils.read_word(self.arg)
        self.arg = rest
        return word

    @property
    def rest(self):
        return self.arg


class SpellCtx(BaseCtx):
    def __init__(self, sn, level, ch, victim, target):
        super().__init__(ch)
        self.sn = sn
        self.level = level
        self.target = victim
        self.target_type = target


def _command_shim(func):
    """One ctx shim per command func (shared across all its registered names)."""
    shim = getattr(func, "_ctx_shim", None)
    if shim is None:
        def shim(ch, argument):
            func(CommandCtx(ch, argument))

        # cmd_type binds do_fun onto Living by __name__ (ch.do_x); keep it.
        shim.__name__ = func.__name__
        shim.__doc__ = func.__doc__
        func._ctx_shim = shim
    return shim


def register(name, func, *, pos, level=0, log=merc.LOG_NORMAL, show=1):
    """Register a ctx-style command under ONE name.

    Maps 1:1 to the old ``interp.register_command(interp.cmd_type(name, func,
    pos, level, log, show))`` call, so a command with several names/aliases
    becomes one ``api.register(...)`` per original registration — preserving each
    name's exact position/level/log/show.
    """
    shim = _command_shim(func)
    interp.register_command(interp.cmd_type(name, shim, pos, level, log, show))
    return func


def command(name, *, pos, level=0, log=merc.LOG_NORMAL, show=1, aliases=()):
    """Decorator sugar for register(): a primary name plus simple aliases."""

    def deco(func):
        register(name, func, pos=pos, level=level, log=log, show=show)
        for alias in aliases:
            register(alias, func, pos=pos, level=level, log=log, show=0)
        return func

    return deco


def spell(
    name,
    *,
    skill_level,
    rating,
    target,
    min_pos,
    slot,
    min_mana,
    beats,
    noun_damage="",
    msg_off="",
    msg_obj="",
    pgsn=None,
):
    """Register a ctx-style spell. The wrapped func takes a single ctx."""

    def deco(func):
        def shim(sn, lvl, ch, vo, tgt):
            return func(SpellCtx(sn, lvl, ch, vo, tgt))

        shim.__name__ = func.__name__
        const.register_spell(
            const.skill_type(
                name, skill_level, rating, shim, target, min_pos, pgsn,
                slot, min_mana, beats, noun_damage, msg_off, msg_obj,
            )
        )
        return func

    return deco
