"""Populate engine registries from the generated KBK content package.

Replaces database/read/read_tables.py: same target registries, same shapes.
Spell modules register first (they carry the function references); KBK data
then wins every field except the function itself.
"""
import importlib
import pkgutil
import re

from rom24 import const, static_tables, tables
from rom24 import content


def _import_all_spells():
    from rom24 import spells as spells_pkg
    for mod in pkgutil.iter_modules(spells_pkg.__path__):
        if mod.name.startswith("spell_"):
            importlib.import_module(f"rom24.spells.{mod.name}")


def _collapse_ws(name):
    # C group_lookup fails on multi-space names (zealot "class  basics");
    # collapse deliberately — documented deviation from broken compiled truth.
    return re.sub(r"\s+", " ", name)


def register():
    _import_all_spells()
    stock_funs = {name: sk.spell_fun for name, sk in const.skill_table.items() if sk.spell_fun}

    const.skill_table.clear()
    for name, s in content.SKILLS.items():
        const.skill_table[name] = const.skill_type(
            name=s["name"], skill_level=s["skill_level"], rating=s["rating"],
            spell_fun=(stock_funs.get(s["spell_fun"]) or stock_funs.get(name)) if s["spell_fun"] else None,
            target=s["target"], minimum_position=s["minimum_position"],
            pgsn=s["pgsn"], slot=s["slot"], min_mana=s["min_mana"], beats=s["beats"],
            noun_damage=s["noun_damage"], msg_off=s["msg_off"], msg_obj=s["msg_obj"],
        )

    const.guild_table.clear()
    for name in content.CLASS_ORDER:
        c = content.CLASSES[name]
        const.guild_table[name] = const.guild_type(
            name=c["name"], who_name=c["who_name"], attr_prime=None,
            weapon=c["weapon"], guild_rooms=c["guild_rooms"],
            skill_adept=c["skill_adept"], thac0_00=c["thac0_00"], thac0_32=c["thac0_32"],
            hp_min=c["hp_min"], hp_max=c["hp_max"], fMana=c["f_mana"],
            base_group=_collapse_ws(c["base_group"]),
            default_group=_collapse_ws(c["default_group"]),
            align=c["align"], xpadd=c["xpadd"], ctype=c["ctype"],
        )

    const.group_table.clear()
    for name, g in content.GROUPS.items():
        const.group_table[name] = const.group_type(
            name=g["name"], rating=g["rating"], spells=g["spells"])

    const.race_table.clear()
    for name, rc in content.RACES.items():
        const.race_table[name] = const.race_type(**rc)

    const.pc_race_table.clear()
    for name, pr in content.PC_RACES.items():
        const.pc_race_table[name] = const.pc_race_type(
            name=pr["name"], who_name=pr["who_name"], points=pr["xpadd"],
            class_mult={cls: 100 for cls in content.CLASS_ORDER},
            skills=pr["skills"], stats=pr["stats"], max_stats=pr["max_stats"],
            size=pr["size"], classes=pr["classes"], align=pr["align"], xpadd=pr["xpadd"],
        )

    const.title_table.clear()
    const.title_table.update(content.TITLES)

    const.attack_table.clear()
    for name, a in content.ATTACKS.items():
        const.attack_table[name] = const.attack_type(**a)

    const.liq_table.clear()
    for name, lq in content.LIQUIDS.items():
        const.liq_table[name] = const.liq_type(**lq)

    # app tables: use namedtuples exactly like read_tables did
    for table, tup, src in (
        (const.str_app, const.str_app_type, content.STR_APP),
        (const.int_app, const.int_app_type, content.INT_APP),
        (const.wis_app, const.wis_app_type, content.WIS_APP),
        (const.dex_app, const.dex_app_type, content.DEX_APP),
        (const.con_app, const.con_app_type, content.CON_APP),
    ):
        table.clear()
        for k, v in src.items():
            table[k] = tup._make(v)

    const.weapon_table.clear()
    for name, w in content.WEAPONS.items():
        const.weapon_table[name] = const.weapon_type(**w)

    # flag tables (act_flags, plr_flags, etc.) — all use flag_type namedtuples
    for tbl_name, flag in static_tables.FLAG_TABLES.items():
        tbl = getattr(tables, tbl_name)
        tbl.clear()
        for k, v in flag.items():
            tbl[k] = tables.flag_type._make(v) if isinstance(v, (list, tuple)) else v

    # position_table: position_type namedtuple per entry
    tables.position_table.clear()
    for k, v in static_tables.POSITION_TABLE.items():
        tables.position_table[k] = tables.position_type._make(v)

    # sex_table: raw values (no namedtuple)
    tables.sex_table.clear()
    for k, v in static_tables.SEX_TABLE.items():
        tables.sex_table[k] = v

    # size_table: raw list, extend (matches read_tables list-append path)
    del tables.size_table[:]
    tables.size_table.extend(static_tables.SIZE_TABLE)

    # clan_table: clan_type namedtuple per entry
    tables.clan_table.clear()
    for k, v in static_tables.CLAN_TABLE.items():
        tables.clan_table[k] = tables.clan_type._make(v)

    # wiznet_table: wiznet_type namedtuple per entry (lives in const, not tables)
    const.wiznet_table.clear()
    for k, v in static_tables.WIZNET_TABLE.items():
        const.wiznet_table[k] = const.wiznet_type._make(v)
