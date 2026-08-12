import os
import logging

logger = logging.getLogger(__name__)

from rom24 import handler_game
from rom24 import merc
from rom24 import interp
from rom24 import settings
from rom24 import fight
from rom24 import api


def do_delete(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if ch.is_npc():
        return

    if ch.confirm_delete:
        if argument:
            ch.send("Delete status removed.\n")
            ch.confirm_delete = False
            return
        else:
            pfile = os.path.join(settings.PLAYER_DIR, ch.name + ".json")
            handler_game.wiznet("$N turns $Mself into line noise.", ch, None, 0, 0, 0)
            fight.stop_fighting(ch, True)
            ch.do_quit("")
            os.remove(pfile)
            return
    if argument:
        ch.send("Just type delete. No argument.\n")
        return

    ch.send("Type delete again to confirm this command.\n")
    ch.send("WARNING: this command is irreversible.\n")
    ch.send("Typing delete with an argument will undo delete status.\n")
    ch.confirm_delete = True
    handler_game.wiznet("$N is contemplating deletion.", ch, None, 0, 0, ch.trust)


def do_delet(ctx):
    ch = ctx.ch
    argument = ctx.arg
    ch.send("You must type the full command to delete yourself.\n")


api.register("delete", do_delete, pos=merc.POS_STANDING, level=0, log=merc.LOG_ALWAYS, show=1)
api.register("delet", do_delet, pos=merc.POS_DEAD, level=0, log=merc.LOG_ALWAYS, show=0)
