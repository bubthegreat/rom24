# Content Packs — Phase 1 (Data-Layer Pack System) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the static game tables (races, classes, skills, groups, flags, …) load from discoverable **content packs** instead of a single hard-coded data directory, with the base game shipped as `packs/core/`, so a community pack can add a race or class with no core edit — while the game still boots identically.

**Architecture:** Add a pack registry that discovers `packs/*/pack.json` manifests, resolves dependency order, and yields an ordered list of pack data directories. Rework `read_tables` to load each table across those directories in order, merging entries and rejecting silent key collisions. Move the existing table JSON files into `packs/core/`. A broken pack is logged and skipped, not fatal.

**Tech Stack:** Python 3.12+, `uv` for env/test (`uv run pytest`), stdlib `json`, namedtuple tables in `src/rom24/const.py`, existing `SaveToken` registry in `src/rom24/database/tracker.py`.

## Global Constraints

- Python packaging/envs: always `uv` (`uv run pytest`, `uv add`), never pip/poetry.
- Tests boot the world through the session-scoped `booted_world` fixture in `tests/conftest.py` (`init_monitoring()` then `db.boot_db()`); `boot_db` is not idempotent — never call it twice in one session.
- Known-good boot baseline (must not change this phase): 48 areas, 986 NPC templates, 1265 item templates, 3126 rooms, 62 shops, 5096 resets, 7623 instances, 252 helps, 244 socials.
- The full suite `uv run pytest tests` must stay green (currently 23 passing).
- Scope deferral (do NOT do this phase): physically relocating `src/rom24/commands/` and `src/rom24/spells/` code into the pack; per-table JSON Schema validation of data bodies. Those are Phase 1b / Phase 2. This phase declares code dirs in the manifest but does not move code.

---

### Task 1: Pack settings + directory scaffold

**Files:**
- Modify: `src/rom24/settings.py` (add `PACKS_DIR` near `DATA_DIR`, line ~44)
- Create: `src/packs/core/pack.json`
- Create: `src/packs/core/.gitkeep` data dir marker (removed once JSONs move in Task 5)

**Interfaces:**
- Produces: `settings.PACKS_DIR` (str, absolute path to the packs root, env-overridable via `PYROM_PACKS_DIR`, default `os.path.join(SOURCE_DIR, "packs")`).

- [ ] **Step 1: Add the setting**

In `src/rom24/settings.py`, after the `DATA_DIR` definition (~line 44):

```python
PACKS_DIR = os.environ.get("PYROM_PACKS_DIR", os.path.join(SOURCE_DIR, "packs"))
logger.info("PACKS_DIR: %s", PACKS_DIR)
```

- [ ] **Step 2: Create the core manifest**

Create `src/packs/core/pack.json`:

```json
{
    "name": "core",
    "version": "1.0.0",
    "_comment": "Base ROM 2.4 content. Ships the static game tables and (declared in place) the core commands and spells.",
    "provides": ["races", "classes", "skills", "spells", "commands"],
    "depends": [],
    "data_dir": ".",
    "code_dirs": ["rom24.commands", "rom24.spells"]
}
```

- [ ] **Step 3: Commit**

```bash
git add src/rom24/settings.py src/packs/core/pack.json src/packs/core/.gitkeep
git commit -m "feat(packs): add PACKS_DIR setting and core pack manifest"
```

---

### Task 2: Pack discovery + manifest parsing

**Files:**
- Create: `src/rom24/packs.py`
- Test: `tests/test_packs_registry.py`

**Interfaces:**
- Produces:
  - `class Pack` with attributes `name: str`, `path: str`, `version: str`, `depends: list[str]`, `data_dir: str` (absolute path to where table JSONs live for this pack), `code_dirs: list[str]`.
  - `discover_packs(packs_root: str = None) -> list[Pack]` — reads every `<packs_root>/*/pack.json`; a directory without a readable/valid `pack.json` is logged and skipped (returns the rest). Defaults `packs_root` to `settings.PACKS_DIR`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_packs_registry.py
import json
import os

from rom24 import packs


def _write_pack(root, name, manifest):
    d = os.path.join(root, name)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "pack.json"), "w") as fp:
        json.dump(manifest, fp)
    return d


def test_discover_reads_manifest(tmp_path):
    root = str(tmp_path)
    _write_pack(root, "core", {"name": "core", "version": "1.0.0", "depends": [], "data_dir": "."})
    found = packs.discover_packs(root)
    assert len(found) == 1
    p = found[0]
    assert p.name == "core"
    assert p.version == "1.0.0"
    assert p.depends == []
    assert p.data_dir == os.path.join(root, "core")


def test_discover_skips_dir_without_manifest(tmp_path):
    root = str(tmp_path)
    os.makedirs(os.path.join(root, "not_a_pack"), exist_ok=True)
    _write_pack(root, "core", {"name": "core", "version": "1.0.0"})
    found = packs.discover_packs(root)
    assert [p.name for p in found] == ["core"]


def test_discover_skips_broken_manifest(tmp_path):
    root = str(tmp_path)
    d = os.path.join(root, "broken")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "pack.json"), "w") as fp:
        fp.write("{ not valid json")
    _write_pack(root, "core", {"name": "core", "version": "1.0.0"})
    found = packs.discover_packs(root)
    assert [p.name for p in found] == ["core"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_packs_registry.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'rom24.packs'`.

- [ ] **Step 3: Write minimal implementation**

```python
# src/rom24/packs.py
import json
import logging
import os

from rom24 import settings

logger = logging.getLogger(__name__)


class Pack:
    def __init__(self, name, path, version="0.0.0", depends=None, data_dir=".", code_dirs=None):
        self.name = name
        self.path = path
        self.version = version
        self.depends = list(depends or [])
        self.data_dir = os.path.normpath(os.path.join(path, data_dir))
        self.code_dirs = list(code_dirs or [])

    def __repr__(self):
        return "Pack(%s @ %s)" % (self.name, self.path)


def _load_manifest(pack_dir):
    manifest_path = os.path.join(pack_dir, "pack.json")
    if not os.path.isfile(manifest_path):
        return None
    try:
        with open(manifest_path, "r") as fp:
            data = json.load(fp)
    except (ValueError, OSError) as exc:
        logger.error("Skipping pack '%s': bad manifest: %s", pack_dir, exc)
        return None
    name = data.get("name")
    if not name:
        logger.error("Skipping pack '%s': manifest has no 'name'.", pack_dir)
        return None
    return Pack(
        name=name,
        path=pack_dir,
        version=data.get("version", "0.0.0"),
        depends=data.get("depends", []),
        data_dir=data.get("data_dir", "."),
        code_dirs=data.get("code_dirs", []),
    )


def discover_packs(packs_root=None):
    if packs_root is None:
        packs_root = settings.PACKS_DIR
    found = []
    if not os.path.isdir(packs_root):
        logger.warning("Packs root does not exist: %s", packs_root)
        return found
    for name in sorted(os.listdir(packs_root)):
        pack_dir = os.path.join(packs_root, name)
        if not os.path.isdir(pack_dir):
            continue
        pack = _load_manifest(pack_dir)
        if pack is not None:
            found.append(pack)
    return found
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_packs_registry.py -q`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add src/rom24/packs.py tests/test_packs_registry.py
git commit -m "feat(packs): discover and parse pack.json manifests"
```

---

### Task 3: Dependency-ordered load order

**Files:**
- Modify: `src/rom24/packs.py`
- Test: `tests/test_packs_registry.py` (add tests)

**Interfaces:**
- Produces: `resolve_load_order(packs: list[Pack]) -> list[Pack]` — returns packs in an order where every pack appears after its `depends`. `core` (no deps) sorts first among independents; independents keep alphabetical order for determinism. A dependency naming a pack that is not present is logged and ignored (the dependent still loads). A dependency cycle raises `ValueError` naming the cycle.

- [ ] **Step 1: Write the failing test**

```python
# add to tests/test_packs_registry.py
import pytest


def _pack(name, depends=None):
    return packs.Pack(name=name, path="/nonexistent/%s" % name, depends=depends or [])


def test_load_order_respects_depends():
    core = _pack("core")
    addon = _pack("necro", depends=["core"])
    order = packs.resolve_load_order([addon, core])
    assert [p.name for p in order] == ["core", "necro"]


def test_load_order_missing_dep_is_ignored():
    addon = _pack("necro", depends=["nonexistent"])
    order = packs.resolve_load_order([addon])
    assert [p.name for p in order] == ["necro"]


def test_load_order_cycle_raises():
    a = _pack("a", depends=["b"])
    b = _pack("b", depends=["a"])
    with pytest.raises(ValueError):
        packs.resolve_load_order([a, b])
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_packs_registry.py -q`
Expected: FAIL — `AttributeError: module 'rom24.packs' has no attribute 'resolve_load_order'`.

- [ ] **Step 3: Write minimal implementation**

```python
# append to src/rom24/packs.py
def resolve_load_order(packs):
    by_name = {p.name: p for p in packs}
    ordered = []
    done = set()
    visiting = set()

    def visit(pack, chain):
        if pack.name in done:
            return
        if pack.name in visiting:
            raise ValueError("Pack dependency cycle: %s" % " -> ".join(chain + [pack.name]))
        visiting.add(pack.name)
        for dep in pack.depends:
            dep_pack = by_name.get(dep)
            if dep_pack is None:
                logger.warning("Pack '%s' depends on missing pack '%s'; ignoring.", pack.name, dep)
                continue
            visit(dep_pack, chain + [pack.name])
        visiting.discard(pack.name)
        done.add(pack.name)
        ordered.append(pack)

    for pack in sorted(packs, key=lambda p: p.name):
        visit(pack, [])
    return ordered
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_packs_registry.py -q`
Expected: PASS (6 passed).

- [ ] **Step 5: Commit**

```bash
git add src/rom24/packs.py tests/test_packs_registry.py
git commit -m "feat(packs): resolve dependency-ordered pack load order"
```

---

### Task 4: Layered `read_tables` with collision detection

**Files:**
- Modify: `src/rom24/database/read/read_tables.py`
- Test: `tests/test_read_tables_layered.py`

**Interfaces:**
- Consumes: `packs.discover_packs`, `packs.resolve_load_order`, `Pack.data_dir`; the `tables` registry (`SaveToken`) from `src/rom24/database/tracker.py`.
- Produces: `read_tables(listener=None, locs=None, extn=settings.DATA_EXTN)` — `locs` is a list of directories scanned **in order**; when omitted it is derived from `resolve_load_order(discover_packs())` data dirs. For each `SaveToken`, each dir's `<name>.json` is merged into the token's table. A key already present from an **earlier** dir is a collision: raise `ValueError` naming the table, the key, and both source dirs — UNLESS the incoming entry dict carries `"__override__": true` (dict-bodied tables only), in which case it replaces and logs. The single-dir default call (`read_tables()` with real packs) must reproduce today's tables exactly.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_read_tables_layered.py
import json
import os

import pytest

from rom24.database import tracker
from rom24.database.read import read_tables as rt


def _mini_token(monkeypatch):
    """Point the tables registry at a single throwaway dict table for the test."""
    table = {}
    tok = tracker.SaveToken("mini_table", table, None)
    monkeypatch.setattr(tracker, "tables", [tok])
    monkeypatch.setattr(rt, "tables", [tok])
    return table


def _write(dirpath, body):
    os.makedirs(dirpath, exist_ok=True)
    with open(os.path.join(dirpath, "mini_table.json"), "w") as fp:
        json.dump(body, fp)


def test_layers_merge_disjoint_keys(tmp_path, monkeypatch):
    table = _mini_token(monkeypatch)
    a, b = str(tmp_path / "a"), str(tmp_path / "b")
    _write(a, {"elf": {"name": "elf"}})
    _write(b, {"gnome": {"name": "gnome"}})
    rt.read_tables(locs=[a, b])
    assert set(table.keys()) == {"elf", "gnome"}


def test_collision_raises(tmp_path, monkeypatch):
    _mini_token(monkeypatch)
    a, b = str(tmp_path / "a"), str(tmp_path / "b")
    _write(a, {"elf": {"name": "elf"}})
    _write(b, {"elf": {"name": "elf2"}})
    with pytest.raises(ValueError):
        rt.read_tables(locs=[a, b])


def test_override_allows_replace(tmp_path, monkeypatch):
    table = _mini_token(monkeypatch)
    a, b = str(tmp_path / "a"), str(tmp_path / "b")
    _write(a, {"elf": {"name": "elf"}})
    _write(b, {"elf": {"name": "elf2", "__override__": True}})
    rt.read_tables(locs=[a, b])
    assert table["elf"]["name"] == "elf2"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_read_tables_layered.py -q`
Expected: FAIL — `read_tables()` does not accept `locs` / collides differently.

- [ ] **Step 3: Write minimal implementation**

Replace the body of `read_tables` in `src/rom24/database/read/read_tables.py`. Keep the existing listener-driven clear block; change loading to iterate `locs` and detect collisions:

```python
import json
import logging
import os

from rom24 import settings
from rom24.database.tracker import tables

logger = logging.getLogger(__name__)


def _default_locs():
    from rom24 import packs
    ordered = packs.resolve_load_order(packs.discover_packs())
    return [p.data_dir for p in ordered]


def read_tables(listener=None, locs=None, extn=settings.DATA_EXTN):
    if locs is None:
        locs = _default_locs()

    if listener:
        logger.debug("Clearing all tables.")
        for tok in tables:
            if not tok.filter:
                tok.table.clear()
            else:
                affected = tok.filter(tok.table)
                for k in list(tok.table.keys()):
                    if k in affected:
                        del tok.table[k]
        listener.send("Tables cleared. Rebuilding...\n")

    logger.info("    Loading Tables from %d location(s).", len(locs))
    for tok in tables:
        seen_source = {}  # key -> loc that first supplied it
        for loc in locs:
            path = "%s%s" % (os.path.join(loc, tok.name), extn)
            if not os.path.isfile(path):
                continue
            with open(path, "r") as fp:
                data = json.load(fp)
            if isinstance(data, list):
                for v in data:
                    tok.table.append(v)
                continue
            for k, v in data.items():
                if isinstance(k, str) and k.isdigit():
                    k = int(k)
                override = isinstance(v, dict) and v.pop("__override__", False)
                if k in seen_source and not override:
                    raise ValueError(
                        "Table '%s' key %r defined by both %s and %s"
                        % (tok.name, k, seen_source[k], loc)
                    )
                if k in seen_source and override:
                    logger.info("Table '%s' key %r overridden by %s", tok.name, k, loc)
                tok.table[k] = tok.tupletype._make(v) if tok.tupletype else v
                seen_source[k] = loc
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_read_tables_layered.py -q`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add src/rom24/database/read/read_tables.py tests/test_read_tables_layered.py
git commit -m "feat(packs): layer read_tables across pack dirs with collision detection"
```

---

### Task 5: Move core table JSONs into `packs/core/` and boot from packs

**Files:**
- Move: `src/data/*.json` (the 28 table files named by the `SaveToken` registry) → `src/packs/core/`
- Delete: `src/packs/core/.gitkeep`
- Verify: `src/rom24/db.py` boot path calls `read_tables()` with no explicit `loc` (so it uses the pack default)

**Interfaces:**
- Consumes: Task 4 `read_tables` default-locs behavior; Task 1 `packs/core/` manifest.
- Produces: a world that boots entirely from `packs/core/` with byte-identical table contents.

- [ ] **Step 1: Identify and move the table files**

The files to move are exactly the `SaveToken.name` values in `src/rom24/database/tracker.py` (e.g. `race_table.json`, `pc_race_table.json`, `guild_table.json`, `group_table.json`, `skill_table.json`, `weapon_table.json`, `title_table.json`, `str_app.json`, `int_app.json`, `wis_app.json`, `dex_app.json`, `con_app.json`, `attack_table.json`, `wiznet_table.json`, `liq_table.json`, `clan_table.json`, `position_table.json`, `sex_table.json`, `size_table.json`, and the `*_flags.json` files). Move each with `git mv`:

```bash
cd /home/bub/Development/rom24
for n in clan_table position_table sex_table size_table act_flags plr_flags \
         affect_flags off_flags imm_flags form_flags part_flags comm_flags \
         race_table pc_race_table skill_table group_table guild_table weapon_table \
         title_table str_app int_app wis_app dex_app con_app attack_table \
         wiznet_table liq_table exit_flags; do
  if [ -f "src/data/$n.json" ]; then git mv "src/data/$n.json" "src/packs/core/$n.json"; fi
done
git rm src/packs/core/.gitkeep
```

- [ ] **Step 2: Confirm the boot call uses the default locs**

Read `src/rom24/db.py` around the `read_tables` call (the agent map cited `db.py:29`). It must call `read_tables()` (or `read_tables(listener)`) with NO `loc=` argument so it falls through to `_default_locs()`. If it passes `loc=DATA_DIR`, remove that argument.

- [ ] **Step 3: Boot and diff world counts**

Run:

```bash
timeout 40 uv run python -c "
from rom24.hotfix import init_monitoring; init_monitoring()
from rom24 import db, const
db.boot_db()
print('races', len(const.race_table))
print('pc_races', len(const.pc_race_table))
print('guilds', len(const.guild_table))
print('skills', len(const.skill_table))
"
```

Expected: non-zero counts matching a pre-move baseline (capture the same numbers by running this against the current tree BEFORE the move). Any table dropping to 0 means its JSON was missed by the move.

- [ ] **Step 4: Run the full suite**

Run: `uv run pytest tests -q`
Expected: PASS — still 23 passed (26+ with the new pack tests). Boot-derived counts in `tests/test_e2e_smoke.py::test_world_booted` unchanged.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat(packs): ship core tables as packs/core; boot tables from packs"
```

---

### Task 6: Isolate a bad pack (non-fatal) + load summary

**Files:**
- Modify: `src/rom24/database/read/read_tables.py` (wrap per-loc loading)
- Test: `tests/test_read_tables_layered.py` (add test)

**Interfaces:**
- Produces: a malformed `<name>.json` in one pack dir is logged with the file path and skipped; the remaining dirs and tables still load. Collisions (Task 4) remain a hard error — only parse/IO failures of a single file are isolated.

- [ ] **Step 1: Write the failing test**

```python
# add to tests/test_read_tables_layered.py
def test_bad_file_is_skipped_not_fatal(tmp_path, monkeypatch):
    table = _mini_token(monkeypatch)
    a, b = str(tmp_path / "a"), str(tmp_path / "b")
    os.makedirs(a, exist_ok=True)
    with open(os.path.join(a, "mini_table.json"), "w") as fp:
        fp.write("{ broken json")
    _write(b, {"gnome": {"name": "gnome"}})
    rt.read_tables(locs=[a, b])  # must not raise
    assert "gnome" in table
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_read_tables_layered.py::test_bad_file_is_skipped_not_fatal -q`
Expected: FAIL — `json.load` raises `ValueError` out of `read_tables`.

- [ ] **Step 3: Write minimal implementation**

In `read_tables`, wrap the per-file read in try/except so a parse/IO error on one file is logged and skipped:

```python
            try:
                with open(path, "r") as fp:
                    data = json.load(fp)
            except (ValueError, OSError) as exc:
                logger.error("Skipping bad table file %s: %s", path, exc)
                continue
```

(Place this in the `for loc in locs:` loop, replacing the plain `with open(...)` block. Keep the collision `raise ValueError` intact — that is a content conflict, not a file error.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_read_tables_layered.py -q`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
git add src/rom24/database/read/read_tables.py tests/test_read_tables_layered.py
git commit -m "feat(packs): isolate a bad table file instead of aborting boot"
```

---

### Task 7: Community-pack integration test (the payoff)

**Files:**
- Test: `tests/test_pack_adds_race.py`

**Interfaces:**
- Consumes: `packs.discover_packs`, `packs.resolve_load_order`, `read_tables` layered loading, the real `packs/core/` data.
- Produces: proof that a second pack adds a playable race with no core edit, and that a duplicate race across packs is rejected.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_pack_adds_race.py
import json
import os
import shutil

import pytest

from rom24 import settings, packs
from rom24.database import tracker
from rom24.database.read import read_tables as rt


def _core_dir():
    return os.path.join(settings.PACKS_DIR, "core")


def test_addon_pack_adds_race(tmp_path, monkeypatch):
    # Assemble a packs root: real core + a tiny addon that adds one race.
    root = str(tmp_path)
    shutil.copytree(_core_dir(), os.path.join(root, "core"))
    addon = os.path.join(root, "zzaddon")
    os.makedirs(addon)
    with open(os.path.join(addon, "pack.json"), "w") as fp:
        json.dump({"name": "zzaddon", "version": "1.0.0", "depends": ["core"], "data_dir": "."}, fp)
    # Minimal race entry matching race_type arity (name, pc_race, act, aff, off, imm, res, vuln, form, parts).
    with open(os.path.join(addon, "race_table.json"), "w") as fp:
        json.dump({"testkin": ["testkin", False, 0, 0, 0, 0, 0, 0, 0, 0]}, fp)

    # Clear the race_table, then load from the assembled root.
    from rom24 import const
    const.race_table.clear()
    ordered = packs.resolve_load_order(packs.discover_packs(root))
    locs = [p.data_dir for p in ordered]
    # Load only the race_table token to keep the test focused.
    race_tok = next(t for t in tracker.tables if t.name == "race_table")
    monkeypatch.setattr(rt, "tables", [race_tok])
    rt.read_tables(locs=locs)

    assert "testkin" in const.race_table
    assert "human" in const.race_table  # core still present


def test_duplicate_race_across_packs_is_rejected(tmp_path):
    root = str(tmp_path)
    shutil.copytree(_core_dir(), os.path.join(root, "core"))
    addon = os.path.join(root, "zzdupe")
    os.makedirs(addon)
    with open(os.path.join(addon, "pack.json"), "w") as fp:
        json.dump({"name": "zzdupe", "version": "1.0.0", "depends": ["core"], "data_dir": "."}, fp)
    with open(os.path.join(addon, "race_table.json"), "w") as fp:
        json.dump({"human": ["human", True, 0, 0, 0, 0, 0, 0, 0, 0]}, fp)

    ordered = packs.resolve_load_order(packs.discover_packs(root))
    locs = [p.data_dir for p in ordered]
    race_tok = next(t for t in tracker.tables if t.name == "race_table")
    import copy
    race_tok = tracker.SaveToken("race_table", {}, race_tok.tupletype)
    rt_tables = rt.tables
    try:
        rt.tables = [race_tok]
        with pytest.raises(ValueError):
            rt.read_tables(locs=locs)
    finally:
        rt.tables = rt_tables
```

- [ ] **Step 2: Run tests to verify they fail (or pass) meaningfully**

Run: `uv run pytest tests/test_pack_adds_race.py -q`
Expected: PASS if Tasks 2–6 are correct. If FAIL, the message pinpoints the registry/merge gap to fix before proceeding.

- [ ] **Step 3: Commit**

```bash
git add tests/test_pack_adds_race.py
git commit -m "test(packs): a community pack adds a race; duplicates are rejected"
```

---

### Task 8: Full-suite green + boot-count gate

**Files:** none (verification only)

- [ ] **Step 1: Run the whole suite**

Run: `uv run pytest tests -q`
Expected: PASS — the original 23 plus the new pack/registry tests, zero failures.

- [ ] **Step 2: Live boot sanity**

Run:

```bash
timeout 40 uv run python -c "
from rom24.hotfix import init_monitoring; init_monitoring()
from rom24 import db; db.boot_db(); print('BOOT_OK')
" 2>&1 | grep -E 'BOOT_OK|Loaded 48 Areas|Traceback'
```

Expected: `BOOT_OK` and `Loaded 48 Areas` present; no `Traceback`.

- [ ] **Step 3: Final commit (if any stragglers)**

```bash
git add -A && git commit -m "chore(packs): phase 1 verification pass" || echo "nothing to commit"
```

---

## Self-Review

**Spec coverage (Phase 1 slice):**
- Pack discovery + manifests → Tasks 1–2. ✓
- Dependency resolution / load order → Task 3. ✓
- Layered data load replacing single `DATA_DIR` → Tasks 4–5. ✓
- Collision detection with named sources + override → Task 4. ✓
- Isolate-a-bad-module (data files) → Task 6. ✓
- Core-as-a-pack → Tasks 1, 5. ✓
- Community pack adds a race with no core edit → Task 7. ✓
- Boots identically / suite green → Tasks 5, 8. ✓
- Deferred (documented in Global Constraints): physical relocation of `commands/`+`spells/` code; per-table JSON Schema body validation. These belong to Phase 1b/2.

**Placeholder scan:** No TBD/TODO steps; every code step has real code. ✓

**Type consistency:** `Pack` attributes (`name`, `path`, `version`, `depends`, `data_dir`, `code_dirs`) are defined in Task 2 and used consistently in Tasks 3, 5, 7. `discover_packs`/`resolve_load_order` signatures match across tasks. `read_tables(listener, locs, extn)` signature is defined in Task 4 and used unchanged in Tasks 5–7. ✓
