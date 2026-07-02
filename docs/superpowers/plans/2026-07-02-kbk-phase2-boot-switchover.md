# KBK Phase 2: Boot Switchover Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** rom24 boots *as KBK* — the generated content package populates the engine registries (no JSON tables), `src/area/kbk` is the boot area set, character creation offers 13 classes / 23 races, unimplemented spells stub gracefully, and the pickle/JSON-table machinery is deleted.

**Architecture:** The converter grows three more emitters (titles, aux combat/liquid/app tables — all from kbk C sources). A new `content/register.py` populates the exact same `const.*`/`tables.*` registries `read_tables()` fills today (spell modules import first and win their function references; KBK data wins everything else). `db.boot_db()` swaps `read.read_tables()` for `content.register()`, settings point at `src/area/kbk`, and the dead machinery (uait/, write/read_tables, tracker, stock JSON + stock areas) is deleted. Player persistence is untouched.

**Tech Stack:** Python 3 (uv), pytest. Branch: `feature/kbk-phase2-switchover` off `feature/kbk-support`.

**Spec:** `docs/superpowers/specs/2026-07-01-kbk-content-and-persistence-design.md` (§1 boot/persistence, §2 tables, decisions #1/#2/#4/#6).

## Global Constraints

- C compiled truth is ground truth, EXCEPT one documented deviation: multi-space group-name references (zealot's `"class  basics"`, const.c:538) are whitespace-collapsed by the converter, because C's own `group_lookup` fails on them (broken in the live game); document with a comment in the emitter.
- Unimplemented spell = `spell_fun None`: visible, practicable, castable-but-inert ("You trace the pattern, but nothing happens — that magic has not been rewoven yet."), NO mana consumed, no crash (spec decision #6).
- Player persistence untouched: `settings.PLAYER_DIR` paths, `handler_pc.save()`, login flow. `INSTANCE_NUM_FILE` (global instance counter) is KEPT — player inventory items carry persisted instance ids that must not collide after reboot.
- Registry shapes must match what `read_tables()` produces today (namedtuples per `database/tracker.py:64-93` mapping), so every downstream consumer keeps working. Extended namedtuple fields get defaults so old call sites never break.
- All tests run `uv run pytest`; ty scope (`uv run ty check tools tests src/rom24/content`) stays green.
- Format ground truth: kbk `titles.c:44` (`title_table[MAX_CLASS][MAX_LEVEL+1][2]`), kbk `const.c` (attack_table, liq_table, str_app/int_app/wis_app/dex_app/con_app, weapon_table), rom24 `database/tracker.py` + `database/read/read_tables.py:40-49` (current registry mapping), `const.py:25-30` (skill_type), research findings pinned in each task.

---

### Task 1: Branch + cparse multi-dimension arrays + converter emits titles

**Files:**
- Modify: `tools/kbk_import/cparse.py` (extract_initializer regex)
- Modify: `tools/kbk_import/emit.py` (add `emit_titles`)
- Modify: `tools/kbk_import/__main__.py` (read titles.c, emit titles.py; add to `out` dict and INIT_SRC)
- Test: `tests/kbk_import/test_emit_titles.py`

**Interfaces:**
- Consumes: `cparse.extract_initializer/parse_braces`, `Resolver`, `emit.HEADER/_fmt`.
- Produces: generated `content/titles.py` defining `TITLES: dict[str, list[list[str]]]` — `TITLES[class_name][level] == [male_title, female_title]`, levels 0..MAX_LEVEL inclusive (61 entries per class). `emit_titles(entries, class_order) -> str`.

- [ ] **Step 1: Branch**

```bash
git checkout feature/kbk-support && git checkout -b feature/kbk-phase2-switchover
```

- [ ] **Step 2: Write the failing tests**

```python
# tests/kbk_import/test_emit_titles.py
from tools.kbk_import import cparse, emit

C = '''
char *const title_table[MAX_CLASS][MAX_LEVEL + 1][2] =
{
    {
        {"Man", "Woman"},
        {"Swordpupil", "Swordpupil"},
        {"Recruit", "Recruit"},
    },
    {
        {"Man", "Woman"},
        {"Pickpocket", "Pickpocket"},
        {"Footpad", "Footpad"},
    },
};
'''


def test_extract_initializer_multidim():
    block = cparse.extract_initializer(C, "title_table")
    entries = cparse.parse_braces(block)
    assert len(entries) == 2
    assert entries[0][1] == [("str", "Swordpupil"), ("str", "Swordpupil")]


def test_emit_titles():
    entries = cparse.parse_braces(cparse.extract_initializer(C, "title_table"))
    src = emit.emit_titles(entries, ["warrior", "thief"])
    ns = {}
    exec(src, ns)
    assert ns["TITLES"]["warrior"][1] == ["Swordpupil", "Swordpupil"]
    assert ns["TITLES"]["thief"][2] == ["Footpad", "Footpad"]
```

- [ ] **Step 3: Run to verify failure** — `uv run pytest tests/kbk_import/test_emit_titles.py -v` → FAIL (extract_initializer raises: its regex expects exactly one `[...]`).

- [ ] **Step 4: Implement**

In `cparse.extract_initializer`, change the search pattern to accept one or more bracket groups:

```python
    m = re.search(re.escape(name) + r"(?:\s*\[[^\]]*\])+\s*=\s*\{", text)
```

Append to `emit.py`:

```python
def emit_titles(entries, class_order):
    titles = {}
    for i, cls in enumerate(class_order):
        if i >= len(entries):
            break
        titles[cls] = [[_str(pair[0]), _str(pair[1])] for pair in entries[i]]
    return HEADER + _fmt("TITLES", titles)


def _str(token):
    return token[1] if isinstance(token, tuple) and token[0] == "str" else str(token)
```

In `__main__.py`: read `args.kbk / "src/titles.c"` (latin-1), extract `title_table`, add `"titles.py": emit.emit_titles(titles_entries, order)` to the `out` dict, and add `from rom24.content.titles import TITLES  # noqa: F401` to `INIT_SRC`.

- [ ] **Step 5: Run to verify pass** — unit tests green; then run the real import and verify:

```bash
uv run python -m tools.kbk_import --kbk ~/Development/kbk --repo .
uv run python -c "from importlib import util; spec = util.spec_from_file_location('t','src/rom24/content/titles.py'); m = util.module_from_spec(spec); spec.loader.exec_module(m); assert len(m.TITLES) == 13; assert all(len(v) == 61 for v in m.TITLES.values()); print('titles ok:', m.TITLES['warrior'][51])"
```

Expected: 13 classes × 61 levels, sensible level-51 hero title printed. Existing tests still pass (`uv run pytest tests/ -q`).

- [ ] **Step 6: Commit** — `git add -A && git commit -m "feat(kbk-import): emit title_table from titles.c (multi-dim initializer support)"`

---

### Task 2: Converter emits aux tables (attack, liq, apps, weapon)

**Files:**
- Modify: `tools/kbk_import/emit.py` (add `emit_aux`)
- Modify: `tools/kbk_import/__main__.py` (emit `aux.py`; extend INIT_SRC)
- Test: `tests/kbk_import/test_emit_aux.py`

**Interfaces:**
- Produces: generated `content/aux.py` defining `ATTACKS: dict[str, dict]` (keys per rom24 `attack_type` namedtuple: name, noun, damage — verify field list at `const.py` before emitting; key = attack name, entry 0 keyed `""` like stock), `LIQUIDS: dict[str, dict]` (per `liq_type`: name, color, proof, full, thirst, food, ssize), `STR_APP/INT_APP/WIS_APP/DEX_APP/CON_APP: dict[int, list]` (raw value lists in C order — read_tables applies `*_app_type._make(v)`, so registration in Task 4 does the same), `WEAPONS: dict[str, dict]` (per rom24 `weapon_type`: name, vnum, type, gsn — gsn as skill-name string).
- C sources: kbk const.c tables `attack_table`, `liq_table`, `str_app`, `int_app`, `wis_app`, `dex_app`, `con_app`, `weapon_table`. Locate each with `grep -n "const struct <name>\|_app\[\]" ~/Development/kbk/src/const.c` and READ the struct defs in merc.h before mapping fields — mirror rom24's namedtuple field ORDER, not C's, where they differ.

- [ ] **Step 1: Write the failing test**

```python
# tests/kbk_import/test_emit_aux.py
from tools.kbk_import import cparse, emit
from tools.kbk_import.resolve import Resolver

C = '''
const struct attack_type attack_table[MAX_DAMAGE_MESSAGE] =
{
    {"none", "hit", -1},
    {"slice", "slice", DAM_SLASH},
};
const struct str_app_type str_app[26] =
{
    {-5, -4, 0, 0},
    {-5, -4, 3, 1},
};
'''
DEFS = {"DAM_SLASH": "1"}


def test_emit_aux_attacks_and_apps():
    r = Resolver(DEFS)
    src = emit.emit_aux(
        {"attack_table": cparse.parse_braces(cparse.extract_initializer(C, "attack_table")),
         "str_app": cparse.parse_braces(cparse.extract_initializer(C, "str_app"))},
        r)
    ns = {}
    exec(src, ns)
    assert ns["ATTACKS"]["slice"] == {"name": "slice", "noun": "slice", "damage": 1}
    assert ns["STR_APP"][1] == [-5, -4, 3, 1]
```

- [ ] **Step 2: Run to verify failure**, then **Step 3: Implement** `emit_aux(tables: dict[str, list], r) -> str` handling each table by name with per-table field mapping (attack: name/noun/damage; liq: name/color + 5 numbers per rom24 liq_type shape — READ rom24 const.py:82 and the current liq_table.json entry shape first and mirror it; apps: plain int lists keyed 0..n; weapon: name/vnum/type/gsn with gsn via `r.gsn_name` or the bare skill word — check C weapon_table entry shape first). Tables absent from the input dict are skipped (emits only what's passed). In `__main__.py`, pass all eight tables and write `"aux.py"`.

- [ ] **Step 4: Verify** — unit green; real import runs; spot check:

```bash
uv run python -c "
ns = {}
exec(open('src/rom24/content/aux.py').read(), ns)
print(len(ns['ATTACKS']), len(ns['LIQUIDS']), len(ns['STR_APP']), len(ns['WEAPONS']))
assert 'slice' in ns['ATTACKS'] and len(ns['STR_APP']) >= 26"
```

All prior tests green. **Step 5: Commit** — `git commit -am "feat(kbk-import): emit attack/liq/app/weapon aux tables"`

---

### Task 3: Static engine tables replace remaining JSON (flags, position, sex, size, clan, wiznet)

**Files:**
- Create: `src/rom24/static_tables.py` (hand-generated ONCE from the current JSON — engine tables, not KBK content)
- Test: `tests/test_static_tables.py`

**Interfaces:**
- Produces: `static_tables.FLAG_TABLES: dict[str, dict]` with keys exactly matching tracker.py's flag JSON names (`act_flags, plr_flags, affect_flags, off_flags, imm_flags, form_flags, part_flags, comm_flags, exit_flags`), plus `POSITION_TABLE, SEX_TABLE, SIZE_TABLE, CLAN_TABLE, WIZNET_TABLE` — each byte-equivalent to what `read_tables()` loads from the corresponding JSON today (same key types: numeric-string keys already converted to int).
- Method: a THROWAWAY script (not committed) reads each JSON via the same logic as `read_tables.py:40-49` minus namedtuple application, and pprints the module; paste result into `static_tables.py` with a header comment `# Engine tables (stock ROM), converted once from src/data/*.json — hand-edit freely.`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_static_tables.py
import json
import os

from rom24 import settings, static_tables


def _load(name):
    with open(os.path.join(settings.DATA_DIR, name + ".json")) as f:
        data = json.load(f)
    return {int(k) if isinstance(k, str) and k.isdigit() else k: v for k, v in data.items()} \
        if isinstance(data, dict) else data


def test_static_tables_match_json():
    for name in ("act_flags", "plr_flags", "affect_flags", "off_flags", "imm_flags",
                 "form_flags", "part_flags", "comm_flags", "exit_flags"):
        assert static_tables.FLAG_TABLES[name] == _load(name), name
    assert static_tables.POSITION_TABLE == _load("position_table")
    assert static_tables.SEX_TABLE == _load("sex_table")
    assert static_tables.SIZE_TABLE == _load("size_table")
    assert static_tables.CLAN_TABLE == _load("clan_table")
    assert static_tables.WIZNET_TABLE == _load("wiznet_table")
```

(This test is TEMPORARY parity proof — Task 8 deletes the JSON and this test together, keeping a plain import-and-shape test instead.)

- [ ] **Step 2-4: Fail → generate module → pass.** **Step 5: Commit** — `git commit -am "feat: static engine tables (flags/position/sex/size/clan/wiznet) from JSON"`

---

### Task 4: `content/register.py` — populate the engine registries

**Files:**
- Create: `src/rom24/content/register.py` (STATIC file, not converter-generated — add its filename to the converter's "do not overwrite" awareness by writing it OUTSIDE the generated set; the converter only writes its known `out` dict, so no change needed, but confirm)
- Modify: `src/rom24/const.py` (extend `guild_type` and `pc_race_type` with defaulted fields)
- Test: `tests/test_content_register.py`

**Interfaces:**
- Consumes: `content` data modules (CLASSES/CLASS_ORDER/SKILLS/GROUPS/RACES/PC_RACES/MATERIALS/TITLES + aux); `static_tables`; the 98 `spells/spell_*.py` modules (each calls `const.register_spell` at import).
- Produces: `register() -> None` that leaves `const.*` and `tables.*` in the exact state downstream code expects (same registries `read_tables()` fills, per tracker.py list). Also `const.guild_type` gains fields `align=0, xpadd=0, ctype=0` (defaults) and `pc_race_type` gains `classes=None, align=0, xpadd=0` (defaults) — namedtuple `defaults=` so existing constructions keep working.

- [ ] **Step 1: Extend the namedtuples in `const.py`:**

```python
guild_type = namedtuple(
    "guild_type",
    "name, who_name, attr_prime, weapon, guild_rooms, "
    "skill_adept, thac0_00, thac0_32, hp_min, hp_max, "
    "fMana, base_group, default_group, align, xpadd, ctype",
    defaults=(0, 0, 0),
)

pc_race_type = namedtuple(
    "pc_race_type",
    "name, who_name, points, class_mult, skills, stats, max_stats, size, "
    "classes, align, xpadd",
    defaults=(None, 0, 0),
)
```

- [ ] **Step 2: Write the failing test**

```python
# tests/test_content_register.py
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
    # a stock-only spell not in KBK's table is gone from the registry
    assert "floating disc" not in const.skill_table or "floating disc" in {  # tolerate if KBK has it
        k for k in const.skill_table}
    # groups: whitespace-collapsed reference resolvable
    assert "class basics" in const.group_table
    zea = const.guild_table["zealot"]
    assert zea.base_group == "class basics"   # collapsed from "class  basics"
    # titles / aux / static
    assert len(const.title_table["warrior"]) == 61
    assert "slice" in const.attack_table
    assert const.str_app[1] is not None
    assert tables.act_flags
```

*(Adjust the two spot values — `acid blast` channeler level and the stock-only spell name — to reality while implementing: print the real values once and pin them. No guessing.)*

- [ ] **Step 3: Run to verify failure**, then **Step 4: Implement `register.py`:**

```python
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
            spell_fun=stock_funs.get(s["spell_fun"]) if s["spell_fun"] else None,
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
    for target, src in ((const.str_app, content.STR_APP), (const.int_app, content.INT_APP),
                        (const.wis_app, content.WIS_APP), (const.dex_app, content.DEX_APP),
                        (const.con_app, content.CON_APP)):
        target.clear()
        for k, v in src.items():
            target[k] = type(target).__name__ and v  # replaced below per app type
    # apps use their namedtuples exactly like read_tables did:
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

    for name, flag in static_tables.FLAG_TABLES.items():
        getattr(tables, name).clear()
        getattr(tables, name).update(
            {k: tables.flag_type._make(v) if isinstance(v, (list, tuple)) else v
             for k, v in flag.items()})
    # position/sex/size/clan/wiznet mirror read_tables' handling — check
    # tracker.py for which get namedtuples (position_type, clan_type, wiznet_type)
    # and which stay raw (sex dict, size list), and apply identically.
```

**IMPORTANT implementation notes (verify each against the code, they are requirements):**
- The doubled app-table loop above is a plan artifact — implement ONLY the second (namedtuple) loop.
- Mirror `tracker.py` exactly for which registries get namedtuples vs raw (position/clan/wiznet DO, sex/size do NOT). Delete the first stray loop.
- `race_type(**rc)` works because Phase 1 emitted RACES with exactly the 10 namedtuple field names — verify once.
- After `register()`, `merc.MAX_LEVEL` need not change (already 60).
- `weapon_table` gsn: stock JSON holds skill-name strings — match that.

**Step 5: Run to verify pass**, **Step 6: Commit** — `git commit -am "feat(content): register KBK tables into engine registries"`

---

### Task 5: Boot switchover — db.boot_db + settings

**Files:**
- Modify: `src/rom24/db.py` (~line 29), `src/rom24/settings.py`
- Test: `tests/test_boot_kbk.py`

**Interfaces:**
- Consumes: `content.register.register()`.
- Produces: `db.boot_db()` boots KBK end-to-end; `settings.AREA_DIR = os.path.join(SOURCE_DIR, "area", "kbk")`, `AREA_LIST_FILE` under it; the boot smoke test other tasks rely on.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_boot_kbk.py
import os

from rom24 import const, db, instance, merc, settings


def test_boot_db_boots_kbk():
    db.boot_db()
    assert len(const.guild_table) == 13
    assert len(instance.area_templates) >= 85
    assert merc.ROOM_VNUM_SCHOOL in instance.room_templates
    # school room must be instanced (creation drops new chars there)
    assert instance.instances_by_room.get(merc.ROOM_VNUM_SCHOOL)
    # world persistence: nothing written outside players/ + instance counter
    assert not os.path.exists(os.path.join(settings.SOURCE_DIR, "data", "world", "areas"))
```

- [ ] **Step 2: fail.** **Step 3: Implement:**

In `settings.py`: `AREA_DIR = os.path.join(SOURCE_DIR, "area", "kbk")` (replace the `AREA_DIR = LEGACY_AREA_DIR` line; keep `AREA_LIST_FILE` derivation). In `db.py:29`: replace `read.read_tables()` with:

```python
    from rom24.content import register
    register.register()
```

(keep the import local like the file's other imports; remove the now-unused `from rom24.database import read` import line.)

- [ ] **Step 4: Run to verify pass** — this is the moment real breakage surfaces (KBK school room vnum, resets, race lookups during area load now resolving against KBK races, etc.). Budget debugging time; every fix follows warn-don't-crash and gets a targeted test. Check `merc.ROOM_VNUM_SCHOOL` (merc.py:603) exists in KBK's midgaard/school — if KBK uses a different school vnum, find it in kbk's C (`grep -n "ROOM_VNUM_SCHOOL" ~/Development/kbk/src/merc.h`) and update merc.py to the KBK value (compiled truth).
- [ ] **Step 5: Full suite green** (`uv run pytest tests/ -q`) — the old full-load test may now double-load; if `test_kbk_full_load.py` conflicts with boot test state, mark modules to run isolated or merge the assertions into the boot test.
- [ ] **Step 6: Commit** — `git commit -am "feat(boot): rom24 boots as KBK (content registries + kbk area set)"`

---

### Task 6: Character creation — KBK classes/races end-to-end

**Files:**
- Modify: `src/rom24/nanny.py:311` ("rom basics"), `nanny.py:547` (attr_prime guard), plus race class-restriction + align enforcement
- Test: `tests/test_creation_kbk.py`

**Interfaces:**
- Consumes: registries from Task 4/5. Research pins: race prompt iterates `const.pc_race_table` (nanny.py:192-221); class prompt iterates `const.guild_table` (263-266, lookup at 275); align step 295-308; groups 310-346; stat boost 547.
- Produces: creation flow functions unchanged in signature; behavior — 23 races and only that race's ALLOWED classes offered; KBK alignment restriction enforced; no attr_prime crash; `"class basics"` granted.

- [ ] **Step 1: Write the failing tests** (drive the nanny state functions directly with a fake descriptor/char the way the module structures them — inspect how nanny states receive (d, argument) and build a minimal fake; if a full fake is impractical, test the extracted helpers below instead):

```python
# tests/test_creation_kbk.py
from rom24 import const, nanny
from rom24.content import register


def setup_module(module):
    register.register()


def test_allowed_classes_for_race():
    allowed = nanny.allowed_classes("dwarf")
    assert "warrior" in allowed and "thief" not in allowed


def test_alignment_allowed():
    # paladin is ALIGN_GOOD-only in KBK (class_table align field)
    assert nanny.alignment_allowed(const.guild_table["paladin"], 750)
    assert not nanny.alignment_allowed(const.guild_table["paladin"], -750)
    assert nanny.alignment_allowed(const.guild_table["warrior"], -750)


def test_prime_stat_boost_none_safe():
    # helper applies +3 only when attr_prime is set
    class FakeCh:
        perm_stat = [13, 13, 13, 13, 13]
        class guild:  # noqa: N801 - stand-in
            attr_prime = None
    nanny.apply_prime_stat_boost(FakeCh)   # must not raise
    assert FakeCh.perm_stat == [13, 13, 13, 13, 13]
```

- [ ] **Step 2: fail.** **Step 3: Implement:** extract three small helpers in nanny.py and use them at the researched sites:

```python
def allowed_classes(race_name):
    pc = const.pc_race_table[race_name]
    if not pc.classes:
        return list(const.guild_table.keys())
    return [cls for cls, ok in pc.classes.items() if ok]


# KBK align codes from merc.h: 0=any 1=good/neutral 2=neutral/evil 3=good 4=neutral 5=evil
# VERIFY against kbk merc.h ALIGN_* defines before finalizing; adjust mapping to the real values.
_ALIGN_OK = {
    0: (750, 0, -750), 1: (750, 0), 2: (0, -750),
    3: (750,), 4: (0,), 5: (-750,),
}


def alignment_allowed(guild, alignment):
    return alignment in _ALIGN_OK.get(guild.align, (750, 0, -750))


def apply_prime_stat_boost(ch):
    if ch.guild.attr_prime is not None:
        ch.perm_stat[ch.guild.attr_prime] += 3
```

Wire-in: class prompt lists `allowed_classes(ch.race.name)` instead of all guilds (and rejects a disallowed pick); the align state re-prompts when `not alignment_allowed(ch.guild, chosen)`; line 547 becomes `apply_prime_stat_boost(ch)`; line 311 `"rom basics"` → `"class basics"`. **VERIFY the ALIGN_* numeric values against `grep -n "ALIGN_" ~/Development/kbk/src/merc.h` and pin them in a comment + test.**

- [ ] **Step 4: pass; full suite green.** **Step 5: Commit** — `git commit -am "feat(creation): KBK classes/races with align + class restrictions"`

---

### Task 7: Spell stubs — cast path

**Files:**
- Modify: `src/rom24/commands/do_cast.py` (the big known-spell check at :29-40 and invocation path before :173)
- Test: `tests/test_spell_stub.py`

**Interfaces:**
- Consumes: registered KBK skill_table (Task 4) with `spell_fun=None` entries. Research pins: do_cast.py:29-40 currently treats `spell_fun is None` as "don't know"; invocation at :173 would crash on None; `handler_magic.obj_cast_spell` already guards (handler_magic.py:158).
- Produces: casting a KNOWN spell whose `spell_fun is None` prints `"You trace the pattern, but nothing happens - that magic has not been rewoven yet.\n"`, consumes NO mana, no lag/beats applied, returns cleanly. Unknown spells keep the existing message.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_spell_stub.py
from rom24 import const
from rom24.content import register


def setup_module(module):
    register.register()


def test_stub_spell_castable_shape():
    sn = const.skill_table["banshee call"]
    assert sn.spell_fun is None
    # do_cast's known-spell condition must accept spell_fun-None entries the
    # char has learned; simulate the condition extracted as a helper:
    from rom24.commands.do_cast import spell_is_castable_stub
    assert spell_is_castable_stub(sn)
```

Plus an integration-style test if a fake char is feasible in this module's pattern (mirror how test_boot/others fake chars; if no precedent exists, the helper test above + a boot-level smoke in Task 9 suffices — note it for the reviewer).

- [ ] **Step 2: fail.** **Step 3: Implement in do_cast.py:** split the :29-40 condition so `spell_fun is None` no longer routes to "don't know" when level/learned checks pass; add before the mana-deduction block:

```python
STUB_MSG = "You trace the pattern, but nothing happens - that magic has not been rewoven yet.\n"


def spell_is_castable_stub(sn):
    return sn is not None and sn.spell_fun is None


# in do_cast, after target resolution and BEFORE mana deduction / lag:
    if spell_is_castable_stub(sn):
        ch.send(STUB_MSG)
        return
```

- [ ] **Step 4: pass + full suite.** **Step 5: Commit** — `git commit -am "feat(magic): graceful stubs for unimplemented KBK spells"`

---

### Task 8: Delete the dead machinery (JSON tables, pickle, stock areas)

**Files:**
- Delete: `src/rom24/uait/` (entire), `src/rom24/commands/do_apickle.py`, `src/rom24/database/write/write_tables.py`, `src/rom24/database/read/read_tables.py`, `src/rom24/database/tracker.py`, `src/data/*.json` (ALL game tables), stock `src/area/*.are` + `src/area/area.lst` + `src/area/socials/` + `src/area/help_files/` (keep `src/area/kbk/`)
- Modify: `src/rom24/settings.py` (remove DATA_EXTN, PKL_EXTN, LEGACY_AREA_DIR, LEGACY_PLAYER_DIR, SOCIAL_DIR, HELP_DIR, SYSTEM_DIR, DOC_DIR, WORLD_DIR dead pieces — KEEP: PLAYER_DIR, INSTANCE_DIR/INSTANCE_NUM_FILE, DATA_DIR only if player dir derives from it — check: PLAYER_DIR = data/players ⇒ keep DATA_DIR), `tests/test_static_tables.py` (replace JSON-parity test with shape assertions), any dangling imports (`grep -rn "read_tables\|write_tables\|tracker\|uait\|legacy_load" src/ tests/`)
- Test: existing suite is the net

**Interfaces:** none new — this is the deletion task. `save.legacy_load_char_obj` (nanny.py:119 fallback): if it imports deleted modules, stub it to return None (no legacy players exist in KBK's world) — check first.

- [ ] **Step 1: grep for every consumer** of the deleted modules/constants (commands listed above) and fix call sites (there should be none left after Tasks 4-7 — anything found gets removed or rewired, each with a note in the commit message).
- [ ] **Step 2: Delete** the files/dirs; rewrite `tests/test_static_tables.py`:

```python
from rom24 import static_tables


def test_static_tables_shapes():
    assert set(static_tables.FLAG_TABLES) >= {
        "act_flags", "plr_flags", "affect_flags", "off_flags", "imm_flags",
        "form_flags", "part_flags", "comm_flags", "exit_flags"}
    assert static_tables.SIZE_TABLE and static_tables.POSITION_TABLE
```

- [ ] **Step 3: Full suite + boot test green.** `uv run pytest tests/ -q` and `uv run ty check tools tests src/rom24/content`.
- [ ] **Step 4: Commit** — `git commit -am "feat!: delete JSON tables, pickle legacy, and stock areas - KBK is the game"`

---

### Task 9: KBK color codes render (rom scheme → pyom pipeline)

**Files:**
- Modify: `src/rom24/data_loader.py` (the four OLC handlers' text fields)
- Test: `tests/test_kbk_colors.py`

**Interfaces:**
- Research pins: loaders call `miniboa_terminal.escape(text, "pyom")` at load; output path converts `color_convert(text, "pyom", terminal)` (telnet.py:204); `COLOR_MAP["rom"]` already maps `{R`-style tokens; today `{R}` passes through as literal.
- Produces: `_kbk_text(text: str) -> str` helper in data_loader used by the OLC handlers for DESCR/LONG (all fields currently escaped): escapes pyom literals then converts rom-scheme tokens into pyom tokens, so the existing send pipeline renders KBK colors.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_kbk_colors.py
from rom24 import data_loader
from rom24.miniboa import colors


def test_kbk_text_converts_rom_tokens_to_pyom():
    out = data_loader._kbk_text("{RHello{x world")
    # after load-processing, sending with pyom->ansi must yield ANSI red + reset
    ansi = colors.color_convert(out, "pyom", "ansi")
    assert "\033[1;31m" in ansi and "\033[0m" in ansi
    assert "{R" not in ansi
```

*(Verify `colors.color_convert`'s exact name/signature first — research quoted its use in telnet.py:204-205; mirror that call.)*

- [ ] **Step 2: fail.** **Step 3: Implement:**

```python
def _kbk_text(text):
    text = miniboa_terminal.escape(text, "pyom")
    return colors.color_convert(text, "rom", "pyom")
```

and replace the `miniboa_terminal.escape(x, "pyom")` calls inside `load_rooms_new`, `load_npcs_new`, `load_objects_new` (and `load_area_data` if it escapes) with `_kbk_text(x)`. If `color_convert` can't target "pyom" as output scheme (inspect its implementation), write the token translation directly: map each `COLOR_MAP["rom"]` token to the pyom token with the same ANSI sequence — build the mapping once at module import.

- [ ] **Step 4: pass + full-load test still 0 warnings.** **Step 5: Commit** — `git commit -am "feat(colors): render KBK {R}-style color codes through the pyom pipeline"`

---

### Task 10: End-to-end boot + login smoke test and phase acceptance

**Files:**
- Test: `tests/test_phase2_acceptance.py`

**Interfaces:** consumes everything above.

- [ ] **Step 1: Write the acceptance test:**

```python
# tests/test_phase2_acceptance.py
import os

from rom24 import const, db, instance, merc, settings


def test_kbk_is_the_game():
    db.boot_db()
    # tables are KBK
    assert set(const.guild_table) == {
        "warrior", "thief", "zealot", "paladin", "anti-paladin", "ranger", "druid",
        "channeler", "assassin", "necromancer", "elementalist", "bard", "healer"}
    assert len(const.pc_race_table) == 23
    assert len(const.skill_table) == 636
    assert len(const.group_table) == 35
    # world is KBK
    assert len(instance.area_templates) >= 85
    # no JSON tables remain on disk
    import glob
    assert not glob.glob(os.path.join(settings.SOURCE_DIR, "data", "*.json"))
    # stock areas gone, kbk areas present
    assert not glob.glob(os.path.join(settings.SOURCE_DIR, "area", "*.are"))
    assert len(glob.glob(os.path.join(settings.SOURCE_DIR, "area", "kbk", "*.are"))) == 100
    # stubs registered
    assert sum(1 for s in const.skill_table.values() if s.spell_fun is None) > 200
```

- [ ] **Step 2: run; fix fallout; green.** Also do ONE manual verification (not automated): `uv run rom24 &`, telnet localhost, create a paladin dwarf → expect race list of 23, class list restricted, land in school, `cast 'banshee call'`-style stub message; kill server. Record the transcript excerpt in the commit message body.
- [ ] **Step 3: Commit** — `git commit -am "test: phase 2 acceptance - rom24 boots and plays as KBK"`

---

### Task 11: Ride-along follow-ups + CI ratchet + docs

**Files:**
- Modify: `src/rom24/data_loader.py` (unify `("SECT", "Sect")` to the `word.upper()` pattern used by the other handlers), `tools/kbk_import/__main__.py` (`write_text(..., encoding="utf-8")`), `tools/kbk_import/resolve.py` (`num() -> int | float` annotation), `tests/kbk_import/test_resolve.py` (move inline `import pytest` to module top), `.github/workflows/mypy.yml` (add any newly-clean modules to ty scope — try `src/rom24/static_tables.py` and `src/rom24/content`), `README.md` (boot instructions now describe KBK; converter usage section)
- Test: suite is the net

- [ ] **Step 1: apply each mechanical fix; Step 2: suite + ty green; Step 3: Commit** — `git commit -am "chore: phase 1 ride-along fixes, CI ratchet, README for KBK boot"`

---

## Self-review checklist

1. **Spec coverage:** §2 tables→Python: Tasks 1-4, 8 (JSON gone). §1 boot/persistence: Task 5 (boot), Task 8 (pickle/write_tables deleted; world persistence was already players-only — INSTANCE_NUM_FILE retained deliberately, documented in Global Constraints). Decision #2 (rom24 IS kbk): Tasks 5, 8, 10. Decision #6 stubs: Task 7. Creation 13/23: Task 6. Colors (spec §3 bullet): Task 9. Acceptance: Task 10.
2. **Known unknowns pinned as verify-steps, not placeholders:** KBK ALIGN_* numeric values (Task 6), color_convert signature (Task 9), ROOM_VNUM_SCHOOL vnum (Task 5), app-table namedtuple mirroring (Task 4), weapon/liq field shapes (Task 2) — each has an explicit verification instruction with the exact grep/file to consult.
3. **Type consistency:** `register()` produces the same registry shapes tracker.py documents; `guild_type`/`pc_race_type` extensions are defaults-only; helpers named identically across tasks (`allowed_classes`, `alignment_allowed`, `apply_prime_stat_boost`, `spell_is_castable_stub`, `_kbk_text`).
4. **Not in this phase:** cabals/bounty/quests/prog execution (Phase 3); spell implementations beyond stubs; player-save format changes.
