"""ctx-style pilot: the bash command.

A heavier command that shows the ctx.engine escape hatch: GET_AC and the group
check are not first-class ctx helpers yet, so they go through ctx.engine.
"""
import random

from rom24 import api


@api.command("bash", pos=api.POS_FIGHTING, level=0)
def do_bash(ctx):
    ch = ctx.ch
    arg = ctx.word()
    chance = ctx.skill("bash")
    if (
        chance == 0
        or (ch.is_npc() and not ch.off_flags.is_set(api.OFF_BASH))
        or (not ch.is_npc() and ch.level < ctx.skill_level("bash"))
    ):
        ctx.send("Bashing? What's that?")
        return

    if not arg:
        victim = ctx.fighting
        if not victim:
            ctx.send("But you aren't fighting anyone!")
            return
    else:
        victim = ctx.char_in_room(arg)
        if not victim:
            ctx.send("They aren't here.")
            return

    if victim.position < api.POS_FIGHTING:
        ctx.act("You'll have to let $M get back up first.", None, victim, to=api.TO_CHAR)
        return
    if victim == ch:
        ctx.send("You try to bash your brains out, but fail.")
        return
    if ctx.is_safe(victim):
        return
    if victim.is_npc() and victim.fighting and not ch.is_same_group(victim.fighting):
        ctx.send("Kill stealing is not permitted.")
        return
    if ch.is_affected(api.AFF_CHARM) and ch.master == victim:
        ctx.act("But $N is your friend!", None, victim, to=api.TO_CHAR)
        return

    # modifiers: size and weight
    chance += ch.carry_weight // 250
    chance -= victim.carry_weight // 200
    if ch.size < victim.size:
        chance += (ch.size - victim.size) * 15
    else:
        chance += (ch.size - victim.size) * 10
    # stats
    chance += ch.stat(api.STAT_STR)
    chance -= (victim.stat(api.STAT_DEX) * 4) // 3
    chance -= ctx.engine.state_checks.GET_AC(victim, api.AC_BASH) // 25
    # speed
    if (ch.is_npc() and ch.off_flags.is_set(api.OFF_FAST)) or ch.is_affected(api.AFF_HASTE):
        chance += 10
    if (victim.is_npc() and victim.off_flags.is_set(api.OFF_FAST)) or victim.is_affected(api.AFF_HASTE):
        chance -= 30
    # level
    chance += ch.level - victim.level
    if not victim.is_npc() and chance < victim.get_skill("dodge"):
        chance -= 3 * (victim.get_skill("dodge") - chance)

    # the attack
    if random.randint(1, 99) < chance:
        ctx.act("$n sends you sprawling with a powerful bash!", None, victim, to=api.TO_VICT)
        ctx.act("You slam into $N, and send $M flying!", None, victim, to=api.TO_CHAR)
        ctx.act("$n sends $N sprawling with a powerful bash.", None, victim, to=api.TO_NOTVICT)
        ctx.improve("bash", True, 1)
        ctx.daze(victim, 3 * api.PULSE_VIOLENCE)
        ctx.wait(ctx.skill_beats("bash"))
        victim.position = api.POS_RESTING
        ctx.damage(victim, random.randint(2, 2 + 2 * ch.size + chance // 20), "bash", api.DAM_BASH, False)
    else:
        ctx.damage(victim, 0, "bash", api.DAM_BASH, False)
        ctx.act("You fall flat on your face!", None, victim, to=api.TO_CHAR)
        ctx.act("$n falls flat on $s face.", None, victim, to=api.TO_NOTVICT)
        ctx.act("You evade $n's bash, causing $m to fall flat on $s face.", None, victim, to=api.TO_VICT)
        ctx.improve("bash", False, 1)
        ch.position = api.POS_RESTING
        ctx.wait(ctx.skill_beats("bash") * 3 // 2)
    ctx.check_killer(victim)
