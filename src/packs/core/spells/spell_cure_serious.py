from rom24 import api
from rom24 import const
from rom24 import fight
from rom24 import game_utils
from rom24 import merc


@api.spell(
    "cure serious",
    skill_level={"mage": 53, "cleric": 7, "thief": 53, "warrior": 10},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_DEFENSIVE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(61),
    min_mana=15,
    beats=12,
    noun_damage="",
    msg_off="!Cure Serious!",
    msg_obj="",
)
def spell_cure_serious(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    heal = game_utils.dice(2, 8) + level // 2
    victim.hit = min(victim.hit + heal, victim.max_hit)
    fight.update_pos(victim)
    victim.send("You feel better! \n")
    if ch != victim:
        ch.send("Ok.\n")
