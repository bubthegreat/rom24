import random
from rom24 import api
from rom24 import const
from rom24 import fight
from rom24 import game_utils
from rom24 import handler_magic
from rom24 import merc
from rom24 import update


@api.spell(
    "energy drain",
    skill_level={"mage": 19, "cleric": 22, "thief": 26, "warrior": 23},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_OFFENSIVE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(25),
    min_mana=35,
    beats=12,
    noun_damage="energy drain",
    msg_off="!Energy Drain!",
    msg_obj="",
)
def spell_energy_drain(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    # Drain XP, MANA, HP.
    # Caster gains HP.
    if victim != ch:
        ch.alignment = max(-1000, ch.alignment - 50)

    if handler_magic.saves_spell(level, victim, merc.DAM_NEGATIVE):
        victim.send("You feel a momentary chill.\n")
        return
    if victim.level <= 2:
        dam = ch.hit + 1
    else:
        update.gain_exp(victim, 0 - random.randint(level // 2, 3 * level // 2))
        victim.mana //= 2
        victim.move //= 2
        dam = game_utils.dice(1, level)
        ch.hit += dam

    victim.send("You feel your life slipping away! \n")
    ch.send("Wow....what a rush! \n")
    fight.damage(ch, victim, dam, sn, merc.DAM_NEGATIVE, True)
