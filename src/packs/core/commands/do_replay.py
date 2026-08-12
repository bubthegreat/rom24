import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api


def do_replay(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if ch.is_npc():
        ch.send("You can't replay.\n")
        return
    if not ch.buffer:
        ch.send("You have no tells to replay.\n")
        return
    [ch.send(tell) for tell in ch.buffer]
    ch.buffer = []


api.register("replay", do_replay, pos=merc.POS_SLEEPING, level=0, log=merc.LOG_NORMAL, show=1)
