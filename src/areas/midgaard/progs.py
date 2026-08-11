"""Example area progs for Midgaard.

Bundled WITH the area (not the base game). Importing this file registers the
handlers via the decorators. Progs receive a curated ``ctx`` handle.
"""
from rom24.prog_triggers import on_speech, on_greet


@on_speech(mob=3000, keyword="hello")
def wizard_greets(ctx):
    """The wizard (vnum 3000) answers anyone who says 'hello' in the room."""
    ctx.say("Greetings, traveller. The arcane arts are not for the faint of heart.")


@on_greet(mob=3000)
def wizard_notices(ctx):
    """The wizard eyes each newcomer to the room."""
    ctx.act("$n eyes you with arcane curiosity.")
