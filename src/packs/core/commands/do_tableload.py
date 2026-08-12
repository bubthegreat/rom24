import logging

logger = logging.getLogger(__name__)

from rom24 import api
from rom24 import interp
from rom24 import merc
from rom24 import database


def do_tableload(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if not argument:
        ch.send("Reloading all tables.")
        database.read.read_tables(ch)


api.register("tableload", do_tableload, pos=merc.POS_DEAD, level=merc.ML, log=merc.LOG_ALWAYS, show=1)
