from rom24 import const, tables
from rom24.content import register


def test_register_populates_engine_registries():
    register.register()
    # classes
    assert len(const.guild_table) == 13
    pal = const.guild_table["paladin"]
    assert pal.who_name == "Pal" and pal.attr_prime is None and pal.hp_max == 18
    # races
    assert len(const.pc_race_table) == 23
    assert const.pc_race_table["dwarf"].classes["warrior"] is True
    assert const.race_table["dwarf"].res != 0
    # skills: KBK data wins, stock spell functions wired by name
    assert len(const.skill_table) == 636
    ab = const.skill_table["acid blast"]
    assert callable(ab.spell_fun)
    assert ab.skill_level["channeler"] == 53
    banshee = const.skill_table["banshee call"]
    assert banshee.spell_fun is None          # unimplemented -> stub
    # groups: whitespace-collapsed reference resolvable
    assert "class basics" in const.group_table
    zea = const.guild_table["zealot"]
    assert zea.base_group == "class basics"   # collapsed from "class  basics"
    # titles / aux / static
    assert len(const.title_table["warrior"]) == 61
    assert "slice" in const.attack_table
    assert const.str_app[1] is not None
    assert tables.act_flags
