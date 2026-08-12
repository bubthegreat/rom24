import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api
from rom24 import comm
from rom24 import handler_ch
from rom24 import handler_game


def do_quit(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if ch.is_npc():
        return
    if ch.position == merc.POS_FIGHTING:
        ch.send("No way! You are fighting.\n")
        return
    if ch.position < merc.POS_STUNNED:
        ch.send("You're not DEAD yet.\n")
        return
    ch.send("Alas, all good things must come to an end.\n")
    handler_game.act("$n has left the game.", ch, None, None, merc.TO_ROOM)
    logger.info("%s has quit.", ch.name)
    handler_game.wiznet(
        "$N rejoins the real world.", ch, None, merc.WIZ_LOGINS, 0, ch.trust
    )
    # After extract_char the ch is no longer valid!
    ch.save(logout=True, force=True)
    # save.legacy_save_char_obj(ch)
    id = ch.id
    d = ch.desc
    ch.extract(True)
    if d is not None:
        comm.close_socket(d)

    # toast evil cheating bastards
    for d in merc.descriptor_list[:]:
        tch = handler_ch.CH(d)
        if tch and tch.id == id:
            tch.extract(True)
            comm.close_socket(d)
    return


def do_qui(ctx):
    ch = ctx.ch
    argument = ctx.arg
    ch.send("If you want to QUIT, you have to spell it out.\n")
    return


api.register("quit", do_quit, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1)
api.register("qui", do_qui, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=0)
