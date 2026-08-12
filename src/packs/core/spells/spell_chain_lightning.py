from rom24 import api
from rom24 import const
from rom24 import fight
from rom24 import game_utils
from rom24 import handler_game
from rom24 import handler_magic
from rom24 import merc
from rom24 import instance


@api.spell(
    "chain lightning",
    skill_level={"mage": 33, "cleric": 53, "thief": 39, "warrior": 36},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_OFFENSIVE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(500),
    min_mana=25,
    beats=12,
    noun_damage="lightning",
    msg_off="!Chain Lightning!",
    msg_obj="",
)
def spell_chain_lightning(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    # H first strike */
    handler_game.act(
        "A lightning bolt leaps from $n's hand and arcs to $N.",
        ch,
        None,
        victim,
        merc.TO_ROOM,
    )
    handler_game.act(
        "A lightning bolt leaps from your hand and arcs to $N.",
        ch,
        None,
        victim,
        merc.TO_CHAR,
    )
    handler_game.act(
        "A lightning bolt leaps from $n's hand and hits you! ",
        ch,
        None,
        victim,
        merc.TO_VICT,
    )

    dam = game_utils.dice(level, 6)
    if handler_magic.saves_spell(level, victim, merc.DAM_LIGHTNING):
        dam = dam // 3
    fight.damage(ch, victim, dam, sn, merc.DAM_LIGHTNING, True)
    last_vict = victim
    level = level - 4  # decrement damage */

    # new targets */
    while level > 0:
        found = False
        for tmp_vict_id in ch.in_room.people:
            tmp_vict = instance.characters[tmp_vict_id]
            if (
                not fight.is_safe_spell(ch, tmp_vict, True)
                and tmp_vict is not last_vict
            ):
                found = True
                last_vict = tmp_vict
                handler_game.act(
                    "The bolt arcs to $n! ", tmp_vict, None, None, merc.TO_ROOM
                )
                handler_game.act(
                    "The bolt hits you! ", tmp_vict, None, None, merc.TO_CHAR
                )
                dam = game_utils.dice(level, 6)
                if handler_magic.saves_spell(level, tmp_vict, merc.DAM_LIGHTNING):
                    dam = dam // 3
                fight.damage(ch, tmp_vict, dam, sn, merc.DAM_LIGHTNING, True)
                level = level - 4  # decrement damage */

        if not found:  # no target found, hit the caster */
            if ch == None:
                return

            if last_vict == ch:  # no double hits */
                handler_game.act(
                    "The bolt seems to have fizzled out.", ch, None, None, merc.TO_ROOM
                )
                handler_game.act(
                    "The bolt grounds out through your body.",
                    ch,
                    None,
                    None,
                    merc.TO_CHAR,
                )
                return

            last_vict = ch
            handler_game.act(
                "The bolt arcs to $n...whoops! ", ch, None, None, merc.TO_ROOM
            )
            ch.send("You are struck by your own lightning! \n")
            dam = game_utils.dice(level, 6)
            if handler_magic.saves_spell(level, ch, merc.DAM_LIGHTNING):
                dam = dam // 3
            fight.damage(ch, ch, dam, sn, merc.DAM_LIGHTNING, True)
            level = level - 4  # decrement damage */
            if ch == None:
                return
