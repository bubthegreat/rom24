import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api
from rom24 import game_utils


def do_alias(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if ch.is_npc():
        return

    argument, arg = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)

    if not arg:
        if not ch.alias:
            ch.send("You have no aliases defined.\n")
            return
        ch.send("Your current aliases are:\n")

        for alias, sub in ch.alias.iteritems():
            ch.send("    %s:  %s\n" % (alias, sub))
        return

    if "unalias" == arg or "alias" == arg:
        ch.send("Sorry, that word is reserved.\n")
        return

    if not arg2:
        if arg not in ch.alias:
            ch.send("That alias is not defined.\n")
            return
        ch.send("%s aliases to '%s'.\n" % (arg, ch.alias[arg]))
        return

    if arg2.startswith("delete") or arg2.startswith("prefix"):
        ch.send("That shall not be done!\n")
        return

    if arg2 in ch.alias:
        ch.alias[arg] = arg2
        ch.send("%s is now realiased to '%s'.\n" % (arg, arg2))
        return
    elif len(ch.alias) > merc.MAX_ALIAS:
        ch.send("Sorry, you have reached the alias limit.\n")
        return
    ch.alias[arg] = arg2
    ch.send("%s is now aliased to '%s'.\n" % (arg, arg2))
    return


def do_alia(ctx):
    ch = ctx.ch
    argument = ctx.arg
    ch.send("I'm sorry, alias must be entered in full.\n")
    return

api.register("alias", do_alias, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1)
api.register("alia", do_alia, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=0)
