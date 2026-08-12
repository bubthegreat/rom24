"""Example area progs for Midgaard.

Bundled WITH the area (not the base game). Importing this file registers the
handlers via the decorators. Progs receive a curated ``ctx`` handle.
"""
from rom24.prog_triggers import on_speech, on_greet, on_give, on_death, on_random


@on_speech(mob=3000, keyword="hello")
def wizard_greets(ctx):
    """The wizard (vnum 3000) answers anyone who says 'hello' in the room."""
    ctx.say("Greetings, traveller. The arcane arts are not for the faint of heart.")


@on_greet(mob=3000)
def wizard_notices(ctx):
    """The wizard eyes each newcomer to the room."""
    ctx.act("$n eyes you with arcane curiosity.")


@on_give(mob=3000)
def wizard_thanks(ctx):
    """The wizard thanks the giver for an object."""
    ctx.say("Ah, a gift! You have my thanks.")


@on_death(mob=3000)
def wizard_dies(ctx):
    """The wizard's parting words."""
    ctx.act("$n whispers, 'The magic... fades...' as $e falls.")


@on_random(mob=3000)
def wizard_mutters(ctx):
    """Occasionally the wizard mutters to himself."""
    if ctx.rand(1, 100) <= 5:
        ctx.say("Mumble mumble... where did I put that spellbook...")
