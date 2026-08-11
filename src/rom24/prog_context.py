"""The curated handle a prog receives.

``Ctx`` is the ONLY world surface exposed to prog code. Its method set is the
guardrail: progs act through these helpers rather than reaching into engine
internals. Keep additions deliberate and safe.
"""
import logging
import random

from rom24 import merc, handler_game

logger = logging.getLogger(__name__)


class Ctx:
    def __init__(self, mob=None, actor=None, victim=None, arg="", room=None, obj=None):
        self.mob = mob        # the entity reacting (None for room-only triggers)
        self.actor = actor    # who caused the event (speaker / enterer / killer)
        self.victim = victim
        self.arg = arg or ""
        self.room = room
        self.obj = obj        # the object involved (give trigger)

    # --- output -----------------------------------------------------------
    def say(self, text):
        """The reacting mob says something to the room."""
        if self.mob is not None:
            self.mob.do_say(text)

    def act(self, fmt, target=None):
        """Emit an act() message from the reacting mob (or the actor)."""
        who = self.mob if self.mob is not None else self.actor
        if who is None:
            return
        handler_game.act(fmt, who, None, target if target is not None else self.actor, merc.TO_ROOM)

    def send(self, text):
        """Send a line directly to the actor."""
        if self.actor is not None:
            self.actor.send(text if text.endswith("\n") else text + "\n")

    # --- helpers ----------------------------------------------------------
    def rand(self, low, high):
        return random.randint(low, high)

    def cast(self, spell_name, target=None):
        """Best-effort cast of a named spell from the mob at a target."""
        from rom24 import const

        skill = const.skill_table.get(spell_name)
        if skill is None or not getattr(skill, "spell_fun", None):
            logger.warning("Prog cast: unknown spell %r", spell_name)
            return
        caster = self.mob if self.mob is not None else self.actor
        victim = target if target is not None else self.actor
        try:
            skill.spell_fun(spell_name, caster.level, caster, victim, merc.TARGET_CHAR)
        except Exception:
            logger.exception("Prog cast failed for %r", spell_name)

    def damage(self, target, amount):
        """Deal untyped damage from the mob to a target."""
        from rom24 import fight

        source = self.mob if self.mob is not None else self.actor
        if source is None or target is None:
            return
        try:
            fight.damage(source, target, amount, merc.TYPE_UNDEFINED, merc.DAM_NONE, True)
        except Exception:
            logger.exception("Prog damage failed")
