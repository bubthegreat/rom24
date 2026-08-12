"""ctx-style pilot: the kick command (skill-gated combat)."""
from rom24 import api


@api.command("kick", pos=api.POS_FIGHTING, level=0)
def do_kick(ctx):
    ch = ctx.ch
    if not ch.is_npc() and ch.level < ctx.skill_level("kick"):
        ctx.send("You better leave the martial arts to fighters.")
        return
    if ch.is_npc() and not ch.off_flags.is_set(api.OFF_KICK):
        return

    victim = ctx.fighting
    if not victim:
        ctx.send("You aren't fighting anyone.")
        return

    ctx.wait(ctx.skill_beats("kick"))
    if ctx.skill("kick") > ctx.rand(1, 99):
        ctx.damage(victim, ctx.rand(1, ch.level), "kick", api.DAM_BASH, True)
        ctx.improve("kick", True, 1)
    else:
        ctx.damage(victim, 0, "kick", api.DAM_BASH, True)
        ctx.improve("kick", False, 1)
    ctx.check_killer(victim)
