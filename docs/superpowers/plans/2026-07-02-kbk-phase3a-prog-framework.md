# KBK Phase 3a: Prog Framework Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The `#IMPROGS` bindings loaded since Phase 1 come alive — a prog registry + dispatch layer wired into the engine's event points, all 22 mob progs and 2 room progs ported, the highest-value item progs ported, and the minimal cabal core the guardian progs require.

**Architecture:** A new `rom24/progs/` package: `registry.py` (name→function registration per kind, binding resolution at instance creation, warn-once for unported names), `dispatch.py` (`fire(kind, trigger, target, *args)` honoring C veto semantics), and implementation modules (`mob_progs.py`, `item_progs.py`, `room_progs.py`). Engine event points call `dispatch.fire(...)` exactly where the C engine does (research doc has every site). Guardian progs need a cabal kernel: the 9-entry cabal table, `cabal_lookup`, Pc `cabal`/`quest_credits` fields, and the citems ledger — commands and the rest of the systems are Plan 3b.

**Tech Stack:** Python 3 (uv), pytest. Branch: `feature/kbk-phase3a-progs` off `feature/kbk-phase2-switchover`.

**Ground truth:** `docs/superpowers/research/2026-07-02-kbk-prog-system.md` (trigger semantics, dispatch sites, census, C sources) and `docs/superpowers/research/2026-07-02-kbk-cabal-bounty-quest.md` (cabal kernel). C sources at `~/Development/kbk/src/`.

## Global Constraints

- C compiled truth for trigger placement and veto semantics: MPROG_DEATH/IPROG_DEATH returning True prevents death (victim restored to standing); MPROG_MOVE returning False blocks movement (pre-move); IPROG_SAC/IPROG_GIVE True prevents the action. All other progs are void.
- Graceful degradation (established policy): a binding whose progname isn't registered logs ONE warning at first fire attempt (not per occurrence) and stays inert. Dispatch never crashes the caller: exceptions inside a prog are caught, logged with prog name + target vnum, and treated as no-veto.
- Prog implementations are faithful ports of the C bodies (research doc quotes representatives; read the C source for each port — file:line ranges in the research doc).
- Every dispatch-site task ends with an integration test proving the trigger fires on real KBK content (the census names real vnums per trigger).
- `uv run pytest tests/ -q` green per task; ty scope (`uv run ty check tools tests src/rom24/content src/rom24/static_tables.py src/rom24/progs`) clean; PUSH after every task (user preference).
- Boot stays clean: 87 areas, zero errors; the full-load and phase-2 acceptance tests keep passing.

---

### Task 1: Prog registry + binding resolution

**Files:**
- Create: `src/rom24/progs/__init__.py`, `src/rom24/progs/registry.py`
- Modify: `src/rom24/object_creator.py` (attach resolved progs at create_mobile/create_item; rooms at create_room)
- Test: `tests/progs/test_registry.py` (+ `tests/progs/__init__.py`)

**Interfaces:**
- Produces: `registry.register(kind: str, trigger: str, name: str)` decorator (kind in {"mob","item","room"}; trigger is the progtype word from area data, e.g. "greet_prog"); `registry.resolve(kind, bindings) -> dict[str, list[callable]]` mapping trigger→functions for a template's `(progtype, progname)` tuples, warn-once via a module-level `_warned: set`; `registry.PROG_KINDS`. Instances get `.progs` (dict) attached by object_creator when the template has non-empty `improgs`; instances without bindings get no attribute (dispatch treats missing as empty).

- [ ] **Step 1: Write the failing test**

```python
# tests/progs/test_registry.py
import logging

from rom24.progs import registry


def test_register_and_resolve():
    calls = []

    @registry.register("mob", "greet_prog", "greet_prog_testling")
    def greet_prog_testling(mob, ch):
        calls.append((mob, ch))

    progs = registry.resolve("mob", [("greet_prog", "greet_prog_testling")])
    assert list(progs) == ["greet_prog"]
    progs["greet_prog"][0]("MOB", "CH")
    assert calls == [("MOB", "CH")]


def test_unknown_prog_warns_once(caplog):
    with caplog.at_level(logging.WARNING, logger="rom24.progs.registry"):
        registry.resolve("mob", [("fight_prog", "no_such_prog")])
        registry.resolve("mob", [("fight_prog", "no_such_prog")])
    warnings = [r for r in caplog.records if "no_such_prog" in r.message]
    assert len(warnings) == 1
```

- [ ] **Step 2: fail.** **Step 3: Implement `registry.py`:**

```python
"""Prog registry: name -> function per kind, resolved onto instances at creation.

KBK's #IMPROGS bindings (loaded as (progtype, progname) tuples on templates since
Phase 1) resolve here. Unknown prognames warn once and stay inert.
"""
import logging

logger = logging.getLogger(__name__)

PROG_KINDS = ("mob", "item", "room")
_registry: dict = {kind: {} for kind in PROG_KINDS}
_warned: set = set()


def register(kind, trigger, name):
    def deco(fn):
        _registry[kind][name] = (trigger, fn)
        return fn
    return deco


def resolve(kind, bindings):
    progs: dict = {}
    for progtype, progname in bindings:
        entry = _registry[kind].get(progname)
        if entry is None:
            if (kind, progname) not in _warned:
                _warned.add((kind, progname))
                logger.warning("prog %s/%s not implemented; binding inert", kind, progname)
            continue
        trigger, fn = entry
        if trigger != progtype:
            logger.warning("prog %s bound as %s but registered as %s; using registration",
                           progname, progtype, trigger)
        progs.setdefault(trigger, []).append(fn)
    return progs
```

`__init__.py`: `from rom24.progs import registry  # noqa: F401` plus imports of the (future) implementation modules — add them as later tasks create them.

object_creator wiring (mirror where spec_fun is attached in create_mobile): for each of create_mobile/create_item/create_room, if the template has a non-empty `improgs` attribute, set `instance.progs = registry.resolve(kind, template.improgs)`.

- [ ] **Step 4: pass; boot test still green** (bindings resolve at instance creation now — expect the warn-once lines for all unported names in the boot log; assert the boot test still passes). **Step 5: Commit + push** — `git commit -am "feat(progs): registry with warn-once binding resolution" && git push`

---

### Task 2: Dispatch core with veto semantics

**Files:**
- Create: `src/rom24/progs/dispatch.py`
- Test: `tests/progs/test_dispatch.py`

**Interfaces:**
- Produces: `dispatch.fire(target, trigger, *args) -> bool` — looks up `getattr(target, "progs", None)`, runs each function for `trigger` with `*args`, catches exceptions (log error with prog + target, continue). Return semantics: returns True iff ANY prog returned a veto value for a veto-capable trigger. Veto mapping (from C): `death_prog` → prog returning True = veto; `move_prog` → prog returning False = veto; `sac_prog`/`give_prog` (item) → True = veto. Non-veto triggers always return False. Encode as `VETO_ON_TRUE = {"death_prog", "sac_prog", "give_prog"}`, `VETO_ON_FALSE = {"move_prog"}`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/progs/test_dispatch.py
from rom24.progs import dispatch


class T:
    pass


def _target(trigger, *fns):
    t = T()
    t.progs = {trigger: list(fns)}
    return t


def test_fire_no_progs_returns_false():
    assert dispatch.fire(T(), "greet_prog", "ch") is False


def test_void_trigger_runs_all_and_returns_false():
    seen = []
    t = _target("greet_prog", lambda a: seen.append(("one", a)), lambda a: seen.append(("two", a)))
    assert dispatch.fire(t, "greet_prog", "ch") is False
    assert seen == [("one", "ch"), ("two", "ch")]


def test_death_prog_true_vetoes():
    t = _target("death_prog", lambda killer: True)
    assert dispatch.fire(t, "death_prog", "killer") is True


def test_move_prog_false_vetoes():
    t = _target("move_prog", lambda ch, room, door: False)
    assert dispatch.fire(t, "move_prog", "ch", "room", 0) is True


def test_prog_exception_is_contained(caplog):
    import logging
    def boom(ch):
        raise RuntimeError("prog bug")
    t = _target("greet_prog", boom)
    with caplog.at_level(logging.ERROR, logger="rom24.progs.dispatch"):
        assert dispatch.fire(t, "greet_prog", "ch") is False
    assert any("prog bug" in r.message or "boom" in r.message for r in caplog.records)
```

- [ ] **Step 2: fail.** **Step 3: Implement:**

```python
"""Prog dispatch honoring C veto semantics (see research doc trigger table)."""
import logging

logger = logging.getLogger(__name__)

VETO_ON_TRUE = {"death_prog", "sac_prog", "give_prog"}
VETO_ON_FALSE = {"move_prog"}


def fire(target, trigger, *args):
    progs = getattr(target, "progs", None)
    if not progs or trigger not in progs:
        return False
    veto = False
    for fn in progs[trigger]:
        try:
            result = fn(*args)
        except Exception:
            logger.exception("prog %s on %r failed", getattr(fn, "__name__", fn), target)
            continue
        if trigger in VETO_ON_TRUE and result is True:
            veto = True
        elif trigger in VETO_ON_FALSE and result is False:
            veto = True
    return veto
```

Note the C fires the FIRST prog per trigger (one function pointer per type); KBK area data never binds two same-trigger progs to one vnum (verify with a quick census check and note the result) — the list form is defensive.

- [ ] **Step 4: pass.** **Step 5: Commit + push** — `git commit -am "feat(progs): dispatch core with C veto semantics" && git push`

---

### Task 3: Cabal kernel (table, lookup, Pc fields, messages, guardians, citems)

**Files:**
- Create: `src/rom24/cabal.py`
- Modify: `src/rom24/handler_pc.py` (Pc fields), `src/rom24/db.py` (load citems at boot)
- Test: `tests/test_cabal_kernel.py`

**Interfaces:**
- Produces (consumed by guardian progs in Task 5 and by Plan 3b): `cabal.CABALS` (index 0-9 list of dicts: name, who_name, long_name, hall, item_vnum, max_members — values verbatim from kbk tables.c:42-55 — READ THE C and transcribe exactly, incl. recall vnums as `recall`), `cabal.lookup(name) -> int` (prefix match, 0 on miss — C lookup.c:97-108 semantics), `cabal.MESSAGES` (per-cabal entrygreeting etc. — from C's cabal_messages table; find it in morecabal.c/tables.c and transcribe), `cabal.get_guardian(cabal_idx)` (search npc instances for ACT_INNER_GUARDIAN + matching cabal), `cabal.is_cabal_item(item)`, `cabal.load_items()` / `cabal.save_items()` (citems ledger: `<cabal> <guardian_vnum>` lines, file at `os.path.join(settings.DATA_DIR, "system", "citems.txt")` — create the system dir constant SYSTEM_DIR in settings pointing at data/system, mkdir'd; ledger persists per spec). Pc gains `cabal=0`, `quest_credits=0`, `induct=0` defaults (auto-persisted via to_json).
- NOTE: npc.cabal / room.cabal are raw name WORDS from area data — resolve to index via `cabal.lookup` lazily where compared (guardian progs compare mob.cabal to ch.cabal: normalize both through a helper `cabal.index_of(value)` accepting int|str|0).
- ACT_INNER_GUARDIAN / ACT_OUTER_GUARDIAN: find KBK's act-flag letters for these (merc.h act flag defines) and how rom24's Bit stores mob act flags; add `cabal.is_inner_guardian(npc)` / `is_outer_guardian(npc)` using the correct bit values (verify against a real guardian mob's ACT field in the area data — the census's guardian vnums, e.g. 9901 from midgaard's IMPROGS).

- [ ] **Step 1: failing tests** (transcribe expected values from the C AFTER reading it — pin real values, no guesses):

```python
# tests/test_cabal_kernel.py
from rom24 import cabal


def test_cabal_table_shape():
    assert len(cabal.CABALS) == 10           # index 0 = none
    assert cabal.CABALS[1]["name"] == "ancient"
    assert cabal.CABALS[1]["item_vnum"] == 3801
    assert cabal.CABALS[2]["name"] == "knight"


def test_lookup_prefix():
    assert cabal.lookup("anc") == 1
    assert cabal.lookup("nosuch") == 0


def test_index_of_normalizes():
    assert cabal.index_of("knight") == 2
    assert cabal.index_of(2) == 2
    assert cabal.index_of(0) == 0
    assert cabal.index_of("") == 0


def test_citems_roundtrip(tmp_path, monkeypatch):
    from rom24 import settings
    monkeypatch.setattr(settings, "SYSTEM_DIR", str(tmp_path))
    cabal.save_items([(1, 3800), (2, 4501)])
    assert cabal.load_item_bindings() == [(1, 3800), (2, 4501)]
```

(adjust API names to what you implement — the ledger read/write pair must round-trip; the boot-time `load_items()` that actually creates objects onto guardians is exercised by the boot test in step 4.)

- [ ] **Step 2: fail.** **Step 3: Implement** per the research doc §Cabals; boot wiring: `db.boot_db()` calls `cabal.load_items()` after resets run (guardians must exist) — missing/empty ledger is fine (warn+skip), missing guardian for a binding warns. **Step 4: full suite + boot green.** **Step 5: Commit + push** — `git commit -am "feat(cabal): kernel - table, lookup, Pc fields, citems ledger" && git push`

---

### Task 4: Wire dispatch sites — movement + speech cluster

**Files:**
- Modify: `src/rom24/handler_ch.py` (move path), `src/rom24/handler_room.py` (put), `src/rom24/commands/do_say.py`
- Test: `tests/progs/test_dispatch_sites.py`

**Interfaces:** engine events now call `dispatch.fire` per the C sites (research doc table):
- PRE-move: for each npc in ch's current room with a move_prog: `if dispatch.fire(npc, "move_prog", ch, ch.in_room, door): return` (blocks movement) — C act_move.c:294.
- POST-arrival (order per C act_move.c:486-534): for each char already in room: items they carry with greet_prog fire `(obj, ch)`; mobs with greet_prog fire `(mob, ch)` only if the room has a PC; then ch's carried items with entry_prog fire `(obj)`; if ch is an npc with entry_prog: fire `(ch)`; room entry_prog fires `(room, ch)` (C handler.c:2009 — fires in char_to_room, i.e., also on login/teleport: put it in handler_room.put or the python equivalent of char_to_room so teleports fire it too; note the decision in the report).
- Speech (do_say, after the existing pyprogs emit): mobs in room (not speaker) speech_prog `(mob, ch, text)`; items in room contents and carried by everyone `(obj, ch, text)`; room speech_prog `(room, ch, text)` — C act_comm.c:930-950.

- [ ] **Step 1: failing integration-style tests** — boot-less: construct npc/room/ch fakes is impractical; instead use the real engine: register throwaway test progs via registry.register, bind them onto a real template (e.g. midgaard mob 3000) by appending to its improgs BEFORE object_creator resolution, boot, then simulate: move a test char into the room via the same call path (find how nanny places chars — instance.rooms[...].put(ch)) and assert the test prog fired. Follow the existing boot-test patterns (conftest clear_instance). If full simulation is too heavy, test the extracted hook helpers directly (e.g. a `fire_room_entry(ch, room)` helper unit-tested with fakes) AND rely on Task 7's live acceptance — state the coverage split in the report.
- [ ] **Step 2-4: fail → wire → green** (full suite; boot). **Step 5: Commit + push** — `git commit -am "feat(progs): wire movement + speech dispatch sites" && git push`

---

### Task 5: Wire dispatch sites — combat + pulse + item-action cluster

**Files:**
- Modify: `src/rom24/fight.py` (violence pulse, damage, raw_kill), `src/rom24/update.py` (pulse), equip/get/drop/give/sacrifice command paths (`commands/do_wear.py`, `do_remove.py`, `do_get.py`, `do_drop.py`, `do_give.py`, `do_sacrifice.py` — locate the actual files), new `src/rom24/commands/do_invoke.py`
- Test: `tests/progs/test_dispatch_sites.py` (extend)

**Interfaces (C sites per research doc):**
- Violence pulse: fighting mob with fight_prog + wait<=0 → `fire(mob, "fight_prog", victim)`; each equipped/carried obj of a fighting char with fight_prog → `fire(obj, "fight_prog", ch)`.
- damage(): victim mob with attack_prog → `fire(victim, "attack_prog", attacker)`.
- raw_kill()/death path: BEFORE death proceeds: victim's items with death_prog — `if fire(obj, "death_prog", victim): victim.position = POS_STANDING; return` (veto); then mob death_prog with killer, same veto. Match the C order (items first, fight.c:4026 then 4034).
- update pulse: mobs with pulse_prog `fire(mob, "pulse_prog")`; items with pulse_prog `fire(obj, "pulse_prog", is_tick)` — find rom24's pulse cadence and pass the tick boolean analog; note any cadence difference from C (PULSE_MOBILE vs per-second) in a comment.
- wear/remove/get/drop: fire the corresponding prog post-action `(obj, ch)`. give: `if fire(obj, "give_prog", ch, victim): return` pre-transfer (veto). sacrifice: `if fire(obj, "sac_prog", ch): return` pre-destruction (veto). bribe (gold given to npc): `fire(npc, "bribe_prog", ch, amount)`.
- `do_invoke <item>`: new command — item must be worn; fires `fire(obj, "invoke_prog", ch, argument)`; unknown/unbound item → "Nothing happens."; register in the command table the way other commands register (check interp/command registration pattern).

- [ ] **Steps: failing tests (same strategy as Task 4) → wire → green → commit + push** — `git commit -am "feat(progs): wire combat, pulse, item-action dispatch sites + do_invoke" && git push`

---

### Task 6: Port all mob progs + room progs

**Files:**
- Create: `src/rom24/progs/mob_progs.py`, `src/rom24/progs/room_progs.py` (+ imports in progs/__init__.py)
- Test: `tests/progs/test_mob_progs.py`

**Interfaces:** all 22 mprog_table entries + 2 rprog_table entries from the research doc, ported faithfully from C (`~/Development/kbk/src/mprog.c` / `rprog.c` — read each function). Guardian progs consume Task 3's cabal kernel (`cabal.MESSAGES`, `cabal.get_guardian`, `cabal.is_cabal_item`, quest_credits +3 group reward, `cabal.save_items()`). Where a C body calls systems that don't exist yet (cabal_shudder, do_cb): implement minimal faithful versions in cabal.py (do_cb ≈ cabal-channel say — a room-say fallback with a `# 3b: cabal channel` note is acceptable; cabal_shudder = global info message). Battlefield/centurion/elthian/mercenary/sequestered/animate progs: port the C logic; any C helper missing in python (e.g. specific spell casts) uses existing rom24 equivalents or logs-and-skips with a note.

- [ ] **Steps: per-prog failing tests for the 6 guardian progs (the load-bearing ones — greet says the cabal greeting to same-cabal PCs only; death returns False and moves cabal items per the C logic; move veto blocks non-members — use fakes for mob/ch with the attributes the progs touch) → implement all 24 → full suite green → the boot log's warn-once list shrinks accordingly (assert midgaard 9901's death/greet bindings now resolve) → commit + push** — `git commit -am "feat(progs): port all KBK mob and room progs" && git push`

---

### Task 7: Port priority item progs

**Files:**
- Create: `src/rom24/progs/item_progs.py` (+ import in progs/__init__.py)
- Create: `docs/superpowers/research/item-progs-checklist.md` (the porting checklist for the tail)
- Test: `tests/progs/test_item_progs.py`

**Interfaces:** KBK registers ~148 item prog functions; porting all in one task is not viable. Port by census value:
1. ALL cabal-item progs (give/greet/speech families on cabal items — they interlock with guardians; identify them in iprog.c by the cabal item vnums from cabal.CABALS).
2. sword_infinity's full family (entry/sac — the only sac_prog; exercises both rare triggers).
3. The top-10 most-referenced fight_prog and invoke_prog items by area frequency (grep the #IMPROGS lines, count per progname, list them in the report).
4. Representative wear/remove flavor pairs for the top-5 wear/remove items.
Everything else stays inert (warn-once) and gets a checklist file `docs/superpowers/research/item-progs-checklist.md` enumerating every unported progname with its iprog.c line, for incremental porting like the spells.

- [ ] **Steps: failing tests for the sac/give veto items + 2 representative invoke/fight progs → implement the priority set → full suite green → checklist committed → commit + push** — `git commit -am "feat(progs): port priority item progs; checklist for the tail" && git push`

---

### Task 8: Phase 3a acceptance

**Files:**
- Test: `tests/test_phase3a_acceptance.py`

**Interfaces:** proves the framework live on real content:

```python
# tests/test_phase3a_acceptance.py (shape — pin real vnums while implementing)
def test_boot_resolves_prog_bindings(clear_instance):
    db.boot_db()
    # a guardian mob instance carries resolved progs
    guardian_instances = instance.instances_by_npc.get(9901, [])
    assert guardian_instances
    g = instance.npcs[guardian_instances[0]]
    assert "greet_prog" in g.progs and "death_prog" in g.progs
    # boot produced zero ERROR records (progs must not break resets)
```

Plus: a scripted live-server walk (same pattern as Phase 2's): enter a guardian room and capture the greeting; `invoke` a ported item; verify the move-veto room blocks a non-member; transcript into the commit body. Fix only what blocks the walk; BLOCKED for anything deeper.

- [ ] **Steps: write → run → green → commit + push** — `git commit -am "test: phase 3a acceptance - progs fire on live KBK content" && git push`

---

## Self-review checklist

1. **Coverage vs research doc:** every trigger type has a dispatch site task (movement/speech T4; combat/pulse/item-actions/invoke T5); all 22+2 mob/room progs T6; item progs prioritized with an explicit no-silent-caps checklist T7; guardians' cabal dependencies T3.
2. **Veto semantics** encoded once in dispatch.py and matched to C at each call site (death: restore position; move: block; give/sac: cancel).
3. **Deferred to 3b (recorded):** induct/outcast + cabal commands, bounty system, quest store + rewards + earning hooks, spec_funs, cabal channel (do_cb full version), the item-prog tail.
4. **Known unknowns pinned as verify-steps:** guardian ACT-flag bit letters (T3), rprog entry placement for teleports (T4), pulse cadence mapping (T5), same-trigger multi-binding census (T2).
