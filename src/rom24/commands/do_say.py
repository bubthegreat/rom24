import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import instance
from rom24 import prog_triggers
from rom24.handler_game import act


def do_say(ch, argument):
    if not argument:
        ch.send("Say what?\n")
        return

    act("$n says '$T'", ch, None, argument, merc.TO_ROOM)
    act("You say '$T'", ch, None, argument, merc.TO_CHAR)
    # Fire speech progs for each mob that heard it.
    if ch.in_room is not None:
        for vch_id in ch.in_room.people[:]:
            vch = instance.characters.get(vch_id)
            if vch is not None and vch is not ch and vch.is_npc():
                prog_triggers.fire_speech(vch, ch, argument, ch.in_room)
    return


interp.register_command(
    interp.cmd_type("say", do_say, merc.POS_RESTING, 0, merc.LOG_NORMAL, 1)
)
interp.register_command(
    interp.cmd_type("'", do_say, merc.POS_RESTING, 0, merc.LOG_NORMAL, 0)
)
