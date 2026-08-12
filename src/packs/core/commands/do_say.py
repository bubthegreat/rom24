"""ctx-style pilot: the say command.

Demonstrates output (act) plus the ctx.engine escape hatch (prog firing +
room-people iteration are not yet first-class ctx helpers).
"""
from rom24 import api


@api.command("say", pos=api.POS_RESTING, level=0, aliases=("'",))
def do_say(ctx):
    if not ctx.arg:
        ctx.send("Say what?")
        return

    ctx.act("$n says '$T'", None, ctx.arg, to=api.TO_ROOM)
    ctx.act("You say '$T'", None, ctx.arg, to=api.TO_CHAR)

    # Fire speech progs for each mob that heard it (escape hatch).
    room = ctx.room
    if room is not None:
        for vch_id in room.people[:]:
            vch = ctx.engine.instance.characters.get(vch_id)
            if vch is not None and vch is not ctx.ch and vch.is_npc():
                ctx.engine.prog_triggers.fire_speech(vch, ctx.ch, ctx.arg, room)
