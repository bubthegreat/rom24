"""Repeatable KBK content import: kbk C sources -> generated python modules + areas."""
import argparse
import pathlib
import shutil

from tools.kbk_import import cparse, emit
from tools.kbk_import.resolve import Resolver

INIT_SRC = emit.HEADER + """\
from rom24.content.constants import *  # noqa: F401,F403
from rom24.content.classes import CLASSES, CLASS_ORDER  # noqa: F401
from rom24.content.skills import SKILLS  # noqa: F401
from rom24.content.groups import GROUPS  # noqa: F401
from rom24.content.races import RACES, PC_RACES  # noqa: F401
from rom24.content.materials import MATERIALS  # noqa: F401
from rom24.content.titles import TITLES  # noqa: F401
from rom24.content.aux import ATTACKS, LIQUIDS, STR_APP, INT_APP, WIS_APP, DEX_APP, CON_APP, WEAPONS  # noqa: F401
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kbk", type=pathlib.Path,
                    default=pathlib.Path("~/Development/kbk").expanduser())
    ap.add_argument("--repo", type=pathlib.Path, default=pathlib.Path("."))
    args = ap.parse_args()

    src = (args.kbk / "src/const.c").read_text(encoding="latin-1")
    merc = (args.kbk / "src/merc.h").read_text(encoding="latin-1")
    defines = {**cparse.parse_defines(merc), **cparse.parse_defines(src)}
    r = Resolver(defines)

    def table(name: str):
        return cparse.parse_braces(cparse.extract_initializer(src, name))

    classes_src, order = emit.emit_classes(table("class_table"), r)

    # Read titles.c for title_table
    titles_src = (args.kbk / "src/titles.c").read_text(encoding="latin-1")
    titles_entries = cparse.parse_braces(cparse.extract_initializer(titles_src, "title_table"))

    aux_tables = {
        "attack_table": table("attack_table"),
        "liq_table": table("liq_table"),
        "str_app": table("str_app"),
        "int_app": table("int_app"),
        "wis_app": table("wis_app"),
        "dex_app": table("dex_app"),
        "con_app": table("con_app"),
        "weapon_table": table("weapon_table"),
    }

    out = {
        "constants.py": emit.emit_constants(defines),
        "classes.py": classes_src,
        "skills.py": emit.emit_skills(table("skill_table"), r, order),
        "groups.py": emit.emit_groups(table("group_table"), r, order),
        "races.py": emit.emit_races(table("race_table"), table("pc_race_table"), r, order),
        "materials.py": emit.emit_materials(
            (args.kbk / "area/materials.lst").read_text(encoding="latin-1")),
        "titles.py": emit.emit_titles(titles_entries, order),
        "aux.py": emit.emit_aux(aux_tables, r),
        "__init__.py": INIT_SRC,
    }
    content_dir = args.repo / "src/rom24/content"
    content_dir.mkdir(parents=True, exist_ok=True)
    for fname, text in out.items():
        (content_dir / fname).write_text(text)

    area_dir = args.repo / "src/area/kbk"
    area_dir.mkdir(parents=True, exist_ok=True)
    kbk_area = args.kbk / "area"
    for f in sorted(kbk_area.glob("*.are")):
        shutil.copyfile(f, area_dir / f.name)
    for f in sorted(kbk_area.glob("*.hlp")):
        shutil.copyfile(f, area_dir / f.name)
    shutil.copyfile(kbk_area / "area.lst", area_dir / "area.lst")
    shutil.copyfile(kbk_area / "materials.lst", area_dir / "materials.lst")

    ns: dict = {}
    exec(out["skills.py"], ns)  # noqa: S102

    try:
        from rom24 import spells as _spells_mod  # noqa: PLC0415
        known = {n[len("spell_"):].replace("_", " ")
                 for n in dir(_spells_mod) if n.startswith("spell_")}
        # spells/__init__.py may not re-export spell functions; fall back to file scan
        if not known and hasattr(_spells_mod, "__file__") and _spells_mod.__file__:
            spells_dir = pathlib.Path(_spells_mod.__file__).parent
            known = {f.stem[len("spell_"):].replace("_", " ")
                     for f in spells_dir.glob("spell_*.py")}
    except ImportError:
        known = set()
        print("Note: rom24.spells not importable; unmapped-spell report skipped.")

    unmapped = sorted(s["name"] for s in ns["SKILLS"].values()
                      if s["spell_fun"] and s["spell_fun"] not in known)
    print(f"classes={len(order)} skills={len(ns['SKILLS'])} unmapped_spell_funs={len(unmapped)}")
    for name in unmapped:
        print(f"  unmapped: {name}")


if __name__ == "__main__":
    main()
