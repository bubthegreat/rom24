from rom24 import api
from rom24 import const
from rom24 import fight
from rom24 import merc


@api.spell(
    "heal",
    skill_level={"mage": 53, "cleric": 21, "thief": 33, "warrior": 30},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_DEFENSIVE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(28),
    min_mana=50,
    beats=12,
    noun_damage="",
    msg_off="!Heal!",
    msg_obj="",
)
def spell_heal(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    victim.hit = min(victim.hit + 100, victim.max_hit)
    fight.update_pos(victim)
    victim.send("A warm feeling fills your body.\n")
    if ch != victim:
        ch.send("Ok.\n")
    return
