from rom24 import api
from rom24 import const
from rom24 import fight
from rom24 import game_utils
from rom24 import handler_game
from rom24 import handler_magic
from rom24 import merc
from rom24 import state_checks


@api.spell(
    "dispel good",
    skill_level={"mage": 53, "cleric": 15, "thief": 53, "warrior": 21},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_OFFENSIVE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(512),
    min_mana=15,
    beats=12,
    noun_damage="dispel good",
    msg_off="!Dispel Good!",
    msg_obj="",
)
def spell_dispel_good(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    if not ch.is_npc() and ch.is_good():
        victim = ch

    if state_checks.IS_EVIL(victim):
        handler_game.act("$N is protected by $S evil.", ch, None, victim, merc.TO_ROOM)
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
    if handler_magic.saves_spell(level, victim, merc.DAM_NEGATIVE):
        dam = dam // 2
    fight.damage(ch, victim, dam, sn, merc.DAM_NEGATIVE, True)
