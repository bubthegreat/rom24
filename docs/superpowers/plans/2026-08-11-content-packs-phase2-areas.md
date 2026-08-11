# Content Packs — Phase 2 (Area Folders + JSON Loader) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Convert the 48 stock `.are` areas into per-area JSON folders under `areas/`, load the world from those folders through a new JSON loader that reproduces the exact template/instance state, then delete the legacy `.are` parser — so areas are self-contained, editable content instead of a hard-coded format.

**Architecture:** Templates are the same classes as live instances with `instance_id=None`, and every world class (`Npc`, `Items`, `Room`, `Area`, `Shop`, `Reset`, `Exit`, `ExtraDescrData`, `AFFECT_DATA`, `bit.Bit`) already round-trips through the `instance.to_json` / `instance.from_json` codec. So conversion is: run the legacy loader once, serialize each area's objects to JSON, and write a new loader that deserializes them and repeats the exact hand-off the legacy loader made to `db.boot_db` (register templates; build the Area instance; instance rooms; append resets; relink `pShop`). Steps after `load_areas` (`area_update`→`reset_area`, `setup_exits`) stay unchanged.

**Tech Stack:** Python 3.12+, `uv run pytest`, stdlib `json`, the `instance` codec (`src/rom24/instance.py:95/152`).

## Global Constraints

- Always `uv` (`uv run pytest`, `uv run python`), never pip/poetry.
- Boot baseline that MUST be reproduced exactly by the JSON path: 48 areas, 986 NPC templates, 1265 item templates, 3126 room templates, 62 shops, 5096 resets, 7623 instances, 252 helps, 244 socials.
- Full suite `uv run pytest tests` stays green (currently 35 passing).
- Serialize/deserialize only via `instance.to_json` (as `json.dumps(obj, default=instance.to_json)`) and `instance.from_json` (as `json.loads(js, object_hook=instance.from_json)`) — do not hand-roll field lists.
- Templates keep `spec_fun` as a string; never serialize a live instance's resolved callable.
- Do NOT delete the legacy `.are` loader or the `.are` files until the JSON boot path is verified (Task 7). The converter needs the legacy loader to run.

## File structure

- New: `src/rom24/area_convert.py` — one-shot converter (legacy `.are` → `areas/<name>/` JSON). Kept in-tree as a tool.
- New: `src/rom24/area_loader_json.py` — the JSON area loader (`load_areas_json`).
- New: `src/areas/<name>/` — per-area folders: `area.json`, `rooms.json`, `mobiles.json`, `objects.json`, `resets.json`, `shops.json`.
- New: `src/areas/_global/helps.json`, `src/areas/_global/socials.json` — helps + socials (today parsed from `.are`).
- Modify: `src/rom24/settings.py` (`AREAS_DIR`).
- Modify: `src/rom24/db.py` (call `load_areas_json` instead of `data_loader.load_areas`).
- Delete (Task 8): the `.are` section parsers in `src/rom24/data_loader.py` and `src/area/*.are`.

---

### Task 1: Round-trip spike (de-risk serialization)

**Files:**
- Test: `tests/test_area_roundtrip_spike.py`

**Interfaces:**
- Consumes: `booted_world` fixture; `instance.to_json`/`from_json`.
- Produces: proof that an Npc, Items, and Room template survive `dumps(default=to_json)` → `loads(object_hook=from_json)` with key fields intact and `instance_id` still `None`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_area_roundtrip_spike.py
import json
from rom24 import instance


def _roundtrip(obj):
    js = json.dumps(obj, default=instance.to_json)
    return json.loads(js, object_hook=instance.from_json)


def test_npc_template_roundtrips(booted_world):
    vnum = next(iter(instance.npc_templates))
    tmpl = instance.npc_templates[vnum]
    back = _roundtrip(tmpl)
    assert back.vnum == tmpl.vnum
    assert back.name == tmpl.name
    assert back.short_descr == tmpl.short_descr
    assert back.level == tmpl.level
    assert back.instance_id is None
    assert back._race == tmpl._race


def test_item_template_roundtrips(booted_world):
    vnum = next(iter(instance.item_templates))
    tmpl = instance.item_templates[vnum]
    back = _roundtrip(tmpl)
    assert back.vnum == tmpl.vnum
    assert back.item_type == tmpl.item_type
    assert list(back.value) == list(tmpl.value)
    assert back.instance_id is None


def test_room_template_roundtrips(booted_world):
    vnum = next(iter(instance.room_templates))
    tmpl = instance.room_templates[vnum]
    back = _roundtrip(tmpl)
    assert back.vnum == tmpl.vnum
    assert back.name == tmpl.name
    assert back.sector_type == tmpl.sector_type
```

- [ ] **Step 2: Run to see pass/fail**

Run: `uv run pytest tests/test_area_roundtrip_spike.py -q`
Expected: PASS if the codec covers these classes; a FAIL pinpoints an un-serializable field (e.g. `pShop`, a bound callable) to strip in the converter before proceeding.

- [ ] **Step 3: If a field fails to round-trip, record it**

If `test_npc_template_roundtrips` fails on `pShop` (a `Shop` back-ref), note it: the converter (Task 3) will set `pShop = None` before dumping mobiles and rebuild it from `shops.json` on load (Task 5). No code change here — this task only proves/《pinpoints》the codec.

- [ ] **Step 4: Commit**

```bash
git add tests/test_area_roundtrip_spike.py
git commit -m "test(areas): prove template JSON round-trip via instance codec"
```

---

### Task 2: AREAS_DIR setting

**Files:**
- Modify: `src/rom24/settings.py`

**Interfaces:**
- Produces: `settings.AREAS_DIR` (env `PYROM_AREAS_DIR`, default `os.path.join(SOURCE_DIR, "areas")`).

- [ ] **Step 1: Add the setting** (after `PACKS_DIR`):

```python
AREAS_DIR = os.environ.get("PYROM_AREAS_DIR", os.path.join(SOURCE_DIR, "areas"))
logger.info("AREAS_DIR: %s", AREAS_DIR)
```

- [ ] **Step 2: Commit**

```bash
git add src/rom24/settings.py
git commit -m "feat(areas): add AREAS_DIR setting"
```

---

### Task 3: Converter — legacy `.are` → `areas/<name>/` JSON

**Files:**
- Create: `src/rom24/area_convert.py`
- Test: `tests/test_area_convert.py`

**Interfaces:**
- Consumes: legacy `data_loader.load_areas()`, `instance.*` collections, `instance.to_json`.
- Produces:
  - `convert_all(out_dir: str = None) -> dict` — assumes the world is already booted (templates populated); writes one folder per area template plus `_global/helps.json` and `_global/socials.json`; returns a summary dict of counts written. `out_dir` defaults to `settings.AREAS_DIR`.
  - Per area folder files: `area.json` (the Area template, incl. `index`), `rooms.json`/`mobiles.json`/`objects.json` (lists of templates whose `.area == area.name`), `resets.json` (the area instance's `reset_list`), `shops.json` (Shops whose keeper vnum belongs to this area's vnum range or whose keeper npc `.area == area.name`).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_area_convert.py
import json
import os
from rom24 import area_convert, instance


def test_convert_writes_area_folders(booted_world, tmp_path):
    out = str(tmp_path)
    summary = area_convert.convert_all(out)
    # one folder per area template
    assert summary["areas"] == len(instance.area_templates)
    # a known area exists with the expected files
    dirs = [d for d in os.listdir(out) if d != "_global"]
    assert dirs, "no area folders written"
    sample = os.path.join(out, dirs[0])
    for fname in ("area.json", "rooms.json", "mobiles.json", "objects.json", "resets.json", "shops.json"):
        assert os.path.isfile(os.path.join(sample, fname)), fname
    # global helps/socials written
    assert os.path.isfile(os.path.join(out, "_global", "helps.json"))
    assert os.path.isfile(os.path.join(out, "_global", "socials.json"))
    # mobiles.json is a JSON list
    with open(os.path.join(sample, "mobiles.json")) as fp:
        assert isinstance(json.load(fp), list)
```

- [ ] **Step 2: Run to verify it fails**

Run: `uv run pytest tests/test_area_convert.py -q`
Expected: FAIL — `ModuleNotFoundError: rom24.area_convert`.

- [ ] **Step 3: Implement the converter**

Create `src/rom24/area_convert.py`. Group templates by `.area` name; pull resets from the matching area **instance** (`instance.areas`); strip `pShop` before dumping mobiles; dump via the codec. Key structure:

```python
import json
import logging
import os

from rom24 import instance, settings, merc

logger = logging.getLogger(__name__)


def _dump(obj):
    return json.loads(json.dumps(obj, default=instance.to_json))


def _safe_name(name):
    return "".join(c if c.isalnum() else "_" for c in name).strip("_").lower()


def _area_instance_for(name):
    for inst in instance.areas.values():
        if getattr(inst, "name", None) == name:
            return inst
    return None


def convert_all(out_dir=None):
    out_dir = out_dir or settings.AREAS_DIR
    os.makedirs(out_dir, exist_ok=True)
    summary = {"areas": 0, "rooms": 0, "mobiles": 0, "objects": 0, "shops": 0, "resets": 0}

    # index shops by keeper vnum -> area name via the keeper npc template
    for name, area_tmpl in instance.area_templates.items():
        folder = os.path.join(out_dir, _safe_name(name))
        os.makedirs(folder, exist_ok=True)

        rooms = [r for r in instance.room_templates.values() if r.area == name]
        mobs = [m for m in instance.npc_templates.values() if m.area == name]
        objs = [o for o in instance.item_templates.values() if o.area == name]
        shops = [s for s in instance.shop_templates.values()
                 if instance.npc_templates.get(s.keeper) is not None
                 and instance.npc_templates[s.keeper].area == name]

        area_inst = _area_instance_for(name)
        resets = list(getattr(area_inst, "reset_list", []) or [])

        # strip pShop back-ref before dumping mobiles (rebuilt on load from shops.json)
        mob_blobs = []
        for m in mobs:
            saved = getattr(m, "pShop", None)
            m.pShop = None
            try:
                mob_blobs.append(_dump(m))
            finally:
                m.pShop = saved

        _write(folder, "area.json", _dump(area_tmpl))
        _write(folder, "rooms.json", [_dump(r) for r in rooms])
        _write(folder, "mobiles.json", mob_blobs)
        _write(folder, "objects.json", [_dump(o) for o in objs])
        _write(folder, "resets.json", [_dump(r) for r in resets])
        _write(folder, "shops.json", [_dump(s) for s in shops])

        summary["areas"] += 1
        summary["rooms"] += len(rooms)
        summary["mobiles"] += len(mobs)
        summary["objects"] += len(objs)
        summary["shops"] += len(shops)
        summary["resets"] += len(resets)

    gdir = os.path.join(out_dir, "_global")
    os.makedirs(gdir, exist_ok=True)
    _write(gdir, "helps.json", _dump(instance.helps))
    _write(gdir, "socials.json", _dump(merc.social_list))
    logger.info("Converted areas: %s", summary)
    return summary


def _write(folder, fname, blob):
    with open(os.path.join(folder, fname), "w") as fp:
        json.dump(blob, fp, indent=2, sort_keys=True)
```

Note: verify the exact module names for helps (`instance.helps`) and socials (`merc.social_list`) against the current tree while implementing; adjust if different. Add `_write` before use or move it above `convert_all`.

- [ ] **Step 4: Run to verify it passes**

Run: `uv run pytest tests/test_area_convert.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/rom24/area_convert.py tests/test_area_convert.py
git commit -m "feat(areas): converter dumps legacy areas to per-area JSON folders"
```

---

### Task 4: Generate the real `src/areas/` tree

**Files:**
- Create: `src/areas/**` (generated output, committed)

- [ ] **Step 1: Run the converter against the real world**

```bash
cd /home/bub/Development/rom24
timeout 60 uv run python -c "
from rom24.hotfix import init_monitoring; init_monitoring()
from rom24 import db, area_convert, settings
db.boot_db()
print(area_convert.convert_all(settings.AREAS_DIR))
"
```

Expected summary: `{'areas': 48, 'rooms': 3126, 'mobiles': 986, 'objects': 1265, 'shops': 62, 'resets': 5096}`. If any number is off, the grouping in Task 3 is wrong (e.g. an area whose `.area` name differs from `area_templates` key) — fix before committing.

- [ ] **Step 2: Sanity-check the tree**

```bash
ls src/areas | head; ls src/areas/_global
find src/areas -name area.json | wc -l   # expect 48
```

- [ ] **Step 3: Commit the generated areas**

```bash
git add src/areas
git commit -m "feat(areas): generate src/areas JSON tree from stock .are files"
```

---

### Task 5: JSON area loader

**Files:**
- Create: `src/rom24/area_loader_json.py`
- Test: `tests/test_area_loader_json.py`

**Interfaces:**
- Consumes: `settings.AREAS_DIR`, `instance.from_json`, `object_creator.create_room`, `world_classes.Area`, `instance.*`.
- Produces: `load_areas_json(areas_dir: str = None)` — deserializes every `areas/<name>/` folder and reproduces the legacy hand-off: for each area, register `area_templates[name]`, build a live `Area` instance (into `instance.areas`/`instances_by_area`), register room/npc/item templates, create each room instance (`create_room`, set `environment`), append resets to the area instance `reset_list`, and relink `npc_templates[keeper].pShop` + `shop_templates[keeper]`. Load `_global/helps.json`/`socials.json` into `instance.helps` / `merc.social_list`. Areas loaded in ascending `area.json:index` order.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_area_loader_json.py
# NOTE: this test boots its OWN world via the JSON loader, so it must run in a
# subprocess-free clean state. Use a dedicated module that does NOT use the
# session booted_world fixture (which uses the legacy loader). Instead assert on
# a fresh in-process load guarded by importing fresh — simplest: assert the
# loader populates the same counts when called after read_tables on a clean set.
import subprocess
import sys


def test_json_boot_matches_baseline():
    code = (
        "from rom24.hotfix import init_monitoring; init_monitoring();"
        "from rom24 import db, instance;"
        "import rom24.db as dbm;"
        "db.boot_db();"
        "print('AREAS', len(instance.area_templates));"
        "print('NPCS', len(instance.npc_templates));"
        "print('ITEMS', len(instance.item_templates));"
        "print('ROOMS', len(instance.room_templates));"
    )
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=90).stdout
    assert "AREAS 48" in out
    assert "NPCS 986" in out
    assert "ITEMS 1265" in out
    assert "ROOMS 3126" in out
```

(This test only becomes meaningful after Task 6 wires `db.boot_db` to the JSON loader; until then it still exercises the legacy path and passes, guarding the counts. Keep it — it is the cutover gate.)

- [ ] **Step 2: Implement the loader**

Create `src/rom24/area_loader_json.py`. Mirror the legacy hand-off precisely (see the grounding: create Area instance eagerly; instance rooms during load; resets on the area instance):

```python
import json
import logging
import os

from rom24 import instance, settings, merc, world_classes, object_creator

logger = logging.getLogger(__name__)


def _load(path):
    with open(path, "r") as fp:
        return json.load(fp, object_hook=instance.from_json)


def _area_dirs(areas_dir):
    dirs = []
    for name in os.listdir(areas_dir):
        d = os.path.join(areas_dir, name)
        if name == "_global" or not os.path.isdir(d):
            continue
        if os.path.isfile(os.path.join(d, "area.json")):
            dirs.append(d)
    # order by the area index recorded in area.json
    def _index(d):
        with open(os.path.join(d, "area.json")) as fp:
            return json.load(fp).get("__class__/rom24.world_classes.Area", {})
    return sorted(dirs, key=lambda d: _area_index(d))


def _area_index(d):
    raw = _load(os.path.join(d, "area.json"))
    return getattr(raw, "index", 0)


def load_areas_json(areas_dir=None):
    areas_dir = areas_dir or settings.AREAS_DIR
    for d in _area_dirs(areas_dir):
        area_tmpl = _load(os.path.join(d, "area.json"))
        instance.area_templates[area_tmpl.name] = area_tmpl
        area_inst = world_classes.Area(area_tmpl)  # live instance -> instance.areas

        for room in _load(os.path.join(d, "rooms.json")):
            instance.room_templates[room.vnum] = room
            room_inst = object_creator.create_room(room)
            room_inst.environment = area_inst.instance_id

        for mob in _load(os.path.join(d, "mobiles.json")):
            instance.npc_templates[mob.vnum] = mob
        for obj in _load(os.path.join(d, "objects.json")):
            instance.item_templates[obj.vnum] = obj

        area_inst.reset_list = _load(os.path.join(d, "resets.json"))

        for shop in _load(os.path.join(d, "shops.json")):
            instance.shop_templates[shop.keeper] = shop
            keeper = instance.npc_templates.get(shop.keeper)
            if keeper is not None:
                keeper.pShop = shop

    gdir = os.path.join(areas_dir, "_global")
    helps = _load(os.path.join(gdir, "helps.json"))
    instance.helps.clear(); instance.helps.update(helps) if isinstance(helps, dict) else instance.helps.extend(helps)
    socials = _load(os.path.join(gdir, "socials.json"))
    merc.social_list.clear(); merc.social_list.update(socials) if isinstance(socials, dict) else merc.social_list.extend(socials)
```

Note: confirm the real container types for `instance.helps` and `merc.social_list` (dict vs list) while implementing and use the matching clear/populate. Confirm `object_creator.create_room` registers into `instance.rooms`/`instances_by_room` (grounding says it does).

- [ ] **Step 3: Standalone loader smoke (no boot wiring yet)**

```bash
timeout 60 uv run python -c "
from rom24.hotfix import init_monitoring; init_monitoring()
from rom24 import instance, area_loader_json
from rom24.database.read import read_tables as rt
rt.read_tables()
area_loader_json.load_areas_json()
print('AREAS', len(instance.area_templates), 'NPCS', len(instance.npc_templates), 'ROOMS', len(instance.room_templates))
"
```

Expected: `AREAS 48 NPCS 986 ROOMS 3126`. Fix loader until counts match.

- [ ] **Step 4: Commit**

```bash
git add src/rom24/area_loader_json.py tests/test_area_loader_json.py
git commit -m "feat(areas): JSON area loader reproducing the legacy hand-off"
```

---

### Task 6: Wire boot to the JSON loader

**Files:**
- Modify: `src/rom24/db.py` (swap `data_loader.load_areas()` for `area_loader_json.load_areas_json()`)

- [ ] **Step 1: Swap the call**

In `src/rom24/db.py`, replace the `data_loader.load_areas()` call in `boot_db` with `area_loader_json.load_areas_json()` (add the import). Leave `area_update()`, `setup_exits()`, and the boot-count logging untouched.

- [ ] **Step 2: Full boot + count gate**

```bash
timeout 60 uv run python -c "
from rom24.hotfix import init_monitoring; init_monitoring()
from rom24 import db; db.boot_db(); print('BOOT_OK')
" 2>&1 | grep -E 'Loaded 48 Areas|986 Npc|1265 Item|3126 Room|62 Shop|5096 Reset|7623 Total Instances|252 Help|244 Social|BOOT_OK|Traceback'
```

Expected: every baseline line present, `BOOT_OK`, no `Traceback`.

- [ ] **Step 3: Full suite**

Run: `uv run pytest tests -q`
Expected: PASS (35 + new area tests). `test_area_loader_json` now exercises the JSON path.

- [ ] **Step 4: Commit**

```bash
git add src/rom24/db.py
git commit -m "feat(areas): boot the world from JSON areas instead of legacy .are"
```

---

### Task 7: End-to-end verification on JSON world

**Files:** none (verification only)

- [ ] **Step 1: Live telnet smoke is covered by `tests/test_e2e_smoke.py`** — confirm combat + save/load still pass on the JSON-booted world:

Run: `uv run pytest tests/test_e2e_smoke.py tests/test_switch_force.py tests/test_spells_fix.py -q`
Expected: PASS.

- [ ] **Step 2: Diff a converted area against its `.are` source spot-check**

Pick Midgaard: confirm a known room (e.g. Temple of Mota vnum 3001) exists with expected name and exits after JSON boot:

```bash
timeout 60 uv run python -c "
from rom24.hotfix import init_monitoring; init_monitoring()
from rom24 import db, instance, merc
db.boot_db()
rid = instance.instances_by_room[3001][0]
r = instance.rooms[rid]
print(repr(r.name), [e for e in range(6) if r.exit[e]])
"
```

Expected: a plausible Temple room name and a non-empty exit list.

---

### Task 8: Delete the legacy `.are` loader and source files

**Files:**
- Modify: `src/rom24/data_loader.py` (remove `.are` section parsers now unused: `load_area`, `load_areas`, `load_npcs`, `load_objects`, `load_rooms`, `load_resets`, `load_shops`, `load_specials`, `load_helps`, `load_socials`; keep anything still referenced elsewhere)
- Delete: `src/area/*.are`, `src/area/area.lst`
- Modify: `src/rom24/settings.py` (drop `LEGACY_AREA_DIR`/`AREA_DIR`/`AREA_LIST_FILE` if now unused)

- [ ] **Step 1: Find residual references**

```bash
grep -rnE "data_loader\.(load_areas|load_area|load_npcs|load_objects|load_rooms|load_resets|load_shops|load_specials|load_helps|load_socials)|LEGACY_AREA_DIR|AREA_LIST_FILE" src/ tests/
```

Only `area_convert.py` (the one-shot tool) and `db.py` (already swapped) should surface. Decide per hit: keep the converter's use (it is the documented migration tool) or gate it behind an explicit call.

- [ ] **Step 2: Remove the dead parsers and `.are` files**

Delete the section-parser functions from `data_loader.py`. `git rm src/area/*.are src/area/area.lst`. If `area_convert.py` still imports them, either keep a minimal legacy reader inside `area_convert.py` or mark the converter as requiring the pre-deletion git history (document at top of file). Preferred: keep the converter working by leaving the `.are` files in a separate `legacy_are/` snapshot dir OR accept the converter is now historical (it already produced `src/areas`). Simplest: keep `area_convert.py` but note it needs the `.are` files which are removed — so move `area_convert.py` to a `tools/` note or delete it too. Choose deletion of both since conversion is done.

- [ ] **Step 3: Boot + full suite gate**

```bash
timeout 60 uv run python -c "from rom24.hotfix import init_monitoring; init_monitoring(); from rom24 import db; db.boot_db(); print('BOOT_OK')" 2>&1 | grep -E 'Loaded 48 Areas|BOOT_OK|Traceback'
uv run pytest tests -q
```

Expected: `BOOT_OK`, 48 areas, suite green.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat(areas): remove legacy .are loader and source files; JSON is canonical"
```

---

## Self-Review

**Spec coverage (Phase 2 slice of the design spec):**
- Area folders + JSON format → Tasks 3–5. ✓
- One-time converter reusing legacy loader → Tasks 3–4. ✓
- New area loader reproducing hand-off → Tasks 5–6. ✓
- Verification gate (boot-count diff vs baseline) → Tasks 4, 6, 7. ✓
- Delete legacy loader → Task 8. ✓
- Helps/socials preserved (they live in `.are`) → converter `_global/` + loader (Tasks 3, 5). ✓

**Placeholder scan:** Two steps (Task 5 helps/socials container type; Task 8 converter-vs-`.are` disposition) say "confirm/decide while implementing" — these are genuine implement-time forks with the options spelled out, not hidden work. All code steps have real code.

**Type consistency:** `load_areas_json(areas_dir=None)`, `convert_all(out_dir=None)`, `Pack`/`instance.*` names consistent across tasks. `_write`/`_dump`/`_load` helpers defined before use. `create_room` hand-off matches the grounding report's step 3/5.
