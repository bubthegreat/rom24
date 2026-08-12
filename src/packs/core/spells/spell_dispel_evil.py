from rom24 import api
from rom24 import const
from rom24 import fight
from rom24 import game_utils
from rom24 import handler_game
from rom24 import handler_magic
from rom24 import merc
from rom24 import state_checks


@api.spell(
    "dispel evil",
    skill_level={"mage": 53, "cleric": 15, "thief": 53, "warrior": 21},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_OFFENSIVE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(22),
    min_mana=15,
    beats=12,
    noun_damage="dispel evil",
    msg_off="!Dispel Evil!",
    msg_obj="",
)
def spell_dispel_evil(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    if not ch.is_npc() and ch.is_evil():
        victim = ch

    if state_checks.IS_GOOD(victim):
        handler_game.act("Mota protects $N.", ch, None, victim, merc.TO_ROOM)
        return

    if state_checks.IS_NEUTRAL(victim):
        handler_game.act(
            "$N does not seem to be affected.", ch, None, victim, merc.TO_CHAR
        )
        return

    if victim.hit > (ch.level * 4):
        dam = game_utils.dice(level, 4)
    else:
        dam = max(victim.hit, game_utils.dice(level, 4))
    if handler_magic.saves_spell(level, victim, merc.DAM_HOLY):
        dam = dam // 2
    fight.damage(ch, victim, dam, sn, merc.DAM_HOLY, True)
