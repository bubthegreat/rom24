import logging

logger = logging.getLogger(__name__)

from rom24 import api
from rom24 import database
from rom24 import merc
from rom24 import interp


def do_tabledump(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if not argument:
        ch.send("Dumping all tables.\n")
        database.write.write_tables(ch)


api.register("tabledump", do_tabledump, pos=merc.POS_DEAD, level=merc.ML, log=merc.LOG_ALWAYS, show=1)
