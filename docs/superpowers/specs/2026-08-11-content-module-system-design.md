# Content Module System — Design Spec

Date: 2026-08-11
Status: Approved (brainstorm), pending implementation plan

## Context

`rom24` is a Python re-authoring of stock ROM 2.4. It is now verified playable
(boots the full world, telnet login, char create, combat, save/load; see the
playable-parity work and `tests/`). The next goal is architectural: make races,
classes, and area programs ("progs") **pluggable content** rather than baked into
the base, so people can add features with guardrails without editing core.

Because nothing is compiled anymore (it is Python), the classic ROM constraints
disappear: content that once had to be part of the C build can instead be
authored as ordinary Python and data files, discovered and loaded at boot.

Intended outcome: a stock base ROM that runs as-is, plus a drop-in module system
where community content (a new class, a new race, an area and the progs it uses)
lives alongside the base and loads through one mechanism. Contributors are
expected to learn Python. OLC (in-game building) is dropped; the standalone KBK
area editor is bundled as the authoring tool instead.

## Decisions (locked during brainstorm)

1. **Module units:** two kinds, one loader — global **content packs** (races,
   classes, skills, spells, commands) and self-contained **area folders** (world
   data + the progs that area uses).
2. **Progs:** real Python functions registered to triggers via decorators, given
   a curated `ctx` handle. The existing custom interpreter in `pyprogs.py` is
   **deleted**.
3. **Area format:** all-JSON, one folder per area. Legacy positional `.are` is
   retired after a one-time conversion. The KBK editor is adapted to read/write
   the JSON format.
4. **Guardrails:** curated `ctx` API surface + existing wall-clock/iteration caps
   for prog execution (no hard sandbox — convention + review). Registry-level
   validation (manifests, JSON Schema, collision detection, isolate-a-bad-module)
   applies to every pack and area.

### Format note: why all-JSON

JSON is already the port's single data format (static tables and
`world_classes.Area` save/load are JSON). Bulk world data is editor-generated,
not hand-typed, so JSON's lack of comments only affects the small hand-edited
manifest, which uses a `"_comment"` field. TOML would add a second parser and
force the editor to emit two formats for a ~10-line ergonomic win. Not worth it.

## Directory layout

```
packs/
  core/                     # the base game, shipped AS a pack (not special-cased)
    pack.json               # manifest: name, version, provides, depends
    races.json  classes.json  groups.json  skills.json
    spells/   *.py          # existing spell modules move here
    commands/ *.py          # existing command modules move here
  <community-pack>/         # e.g. adds a class or race; same shape as core

areas/
  midgaard/
    area.json               # header: name, vnum range, builders, reset timer, requires
    rooms.json  mobiles.json  objects.json  resets.json  shops.json
    progs.py                # real-Python triggers for THIS area
```

"Core is just a pack" keeps one code path and lets an operator swap or extend the
base with the same mechanism community content uses.

## Components

### 1. Loader & registry

Reuse the proven auto-import pattern (`hotfix.init_directory_module` imports every
`.py` in a package; each module self-registers at import via
`interp.register_command` / `const.register_spell`). Extend it:

- **Manifest-driven discovery:** scan `packs/*/pack.json` and `areas/*/area.json`;
  resolve `depends`/`requires`; compute a topological load order.
- **Layered data load:** replace the single `DATA_DIR` scan in
  `read_tables`/`SaveToken` (`src/rom24/database/read/read_tables.py:12`,
  `src/rom24/database/tracker.py`) with a scan across packs in load order; later
  packs add entries; silent clobber is disallowed.
- **Collision detection:** two packs defining the same keyed entry (e.g. race
  `"elf"`) is a hard load error naming both sources, unless one entry declares
  `"override": true`.
- **Isolate a bad module:** each pack and area loads inside try/except; a broken
  one is logged and skipped, boot continues, and it appears in a load summary.
  (Today a single bad area kills boot.)
- **Schema validation:** each `races.json`/`classes.json`/`rooms.json`/etc. is
  validated against a JSON Schema before entering the tables; failures name the
  file and field.

### 2. Area folder format + migration

- `world_classes.Area` already has JSON save/load
  (`src/rom24/world_classes.py`), so the target format largely exists; split its
  single blob into the per-file layout above (`rooms.json`, `mobiles.json`, …).
- **One-time converter:** reuse the *existing* legacy `.are` loader
  (`src/rom24/data_loader.py`) to read all 48 stock areas into memory, then dump
  each as an `areas/<name>/` JSON folder. After conversion the legacy `.are`
  loader is deleted.
- **Verification gate:** boot from the converted JSON and diff world counts
  against the known `.are` baseline (48 areas, 986 NPC templates, 1265 item
  templates, 3126 rooms, 62 shops, 5096 resets, 7623 instances).

### 3. Prog system

- **Delete** the custom interpreter and signal-string bus in `pyprogs.py`.
- **New trigger registry.** `areas/<x>/progs.py` uses decorators bound to vnums:

  ```python
  @on_speech(mob=3001, keyword="heal")
  def priest_heals(ctx):
      ctx.act("$n lays hands on you.")
      ctx.cast("heal", ctx.actor)

  @on_entry(room=3005)
  def trap(ctx):
      if ctx.rand(1, 100) < 20:
          ctx.damage(ctx.actor, 10)
  ```

- **`ctx`** is the only world handle a prog receives: `ctx.actor`, `ctx.victim`,
  `ctx.room`, `ctx.arg`, plus curated methods (`act`, `send`, `rand`, `cast`,
  `damage`, `mob_lookup`, `transfer`, …). The curated surface *is* the guardrail.
- **Trigger set (v1, from ROM mobprogs):** `speech, entry, greet, give, fight,
  hpcnt (low-hp), death, random/tick, act, exit`. Each trigger requires an
  **emit point** wired into the engine — today only `do_say` emits
  (`src/rom24/commands/do_say.py:18`). Wiring these emit points is the bulk of the
  prog work.
- **Execution caps:** keep the existing 200ms wall-clock timeout and
  `settings.MAX_ITERATIONS` cap. A prog that raises is caught, logged with area +
  function name, and the game continues.

### 4. Races & classes as pack data

Races and classes are already pure JSON → namedtuple
(`race_type`/`pc_race_type`/`guild_type` in `src/rom24/const.py`;
`SaveToken` registry in `src/rom24/database/tracker.py`). The only change is that
their *source* moves from `src/data/` into `packs/<pack>/`, and `read_tables`
scans packs. Runtime consumers (`const.race_table`, `nanny.py` char creation, the
`race`/`guild` property resolvers in `src/rom24/living.py`) are untouched. A
community pack adds a race by shipping `races.json` + a `pc_race` entry and a
`pack.json`; no core edit.

### 5. KBK editor integration

- Adapt the editor's parser/writer
  (`/home/bub/Development/kbk/area-editor/src/area_editor/parsers/are_parser.py`,
  `writers/are_writer.py`; Python + DearPyGui) from keyworded `.are` to the JSON
  folder format. Its models (`room/mobile/object/reset/shop/special`) already
  match the data shapes.
- Bundle it as the authoring tool. **OLC is dropped** — no in-game building.
- Editor prog awareness (listing/scaffolding triggers in `progs.py`) is a later
  enhancement; v1 leaves `progs.py` to hand-authoring.

## Guardrails summary

- **Runtime (progs):** curated `ctx` only; wall-clock + iteration caps; exceptions
  isolated per prog.
- **Load time (all modules):** manifest required; JSON Schema validation with
  file/field error messages; key-collision detection with named sources;
  dependency resolution; a broken pack/area skipped (not fatal) and reported.

## Phasing

Each phase ships a working, tested game.

1. **Registry + core pack.** Introduce `packs/core/`; move
   races/classes/groups/skills/spells/commands into it; make `read_tables` do the
   layered pack scan. Game boots identically. Gate: existing 23 tests still pass;
   boot counts unchanged.
2. **Area folders + converter.** Convert the 48 stock `.are` files to
   `areas/<name>/` JSON; write the new area loader; delete the legacy loader.
   Gate: boot-count diff against the `.are` baseline; e2e smoke passes.
3. **Prog system.** Trigger decorators + `ctx` + emit points; delete `pyprogs`
   interpreter. Ship 2–3 example progs in Midgaard, each covered by a test that
   fires the trigger and asserts the effect.
4. **KBK editor.** JSON round-trip (open a converted area, edit, save, reload,
   diff); bundle in-repo or as a documented sibling tool.
5. **Docs + guardrails polish.** Manifest/JSON schemas, contributor guide,
   collision/validation error messages, an example community pack (a new race or
   class) as a worked example and regression fixture.

## Out of scope

- In-game OLC (explicitly dropped).
- KBK-specific gameplay subsystems (assassin/necro/ranger classes, cabals, quest
  store, etc.) — those are separate content packs someone can author later; this
  spec only builds the mechanism.
- Legacy save-system cleanup and other non-module refactors.

## Verification strategy

- **Per phase:** the full `uv run pytest tests` suite stays green; each phase adds
  tests for its new mechanism.
- **Conversion fidelity:** JSON-booted world counts match the `.are` baseline
  exactly.
- **Module system:** tests for load order, dependency resolution, collision
  detection (duplicate race errors), a deliberately-broken pack being skipped
  without killing boot, and an example community pack adding a playable race.
- **Progs:** per-trigger tests that emit the event and assert the `ctx` effect;
  a prog that raises does not crash the tick.
- **End-to-end:** the existing e2e smoke (boot → combat → save/load) plus a new
  smoke that boots entirely from `packs/` + `areas/` with zero legacy `.are`.
