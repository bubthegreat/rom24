# Gameplay Test Suite — Design Spec

Date: 2026-08-12
Status: Approved (brainstorm)

## Context

The ROM 2.4 Python port is now deployed and being played for the first time.
Real play immediately surfaced gameplay bugs (unknown commands not answering
`Huh?`, killing a mob leaves no corpse, `look in <container>` shows nothing).
The port was never playtested before this, so many command/spell/system paths
have latent behavior bugs. Whack-a-mole over telnet does not scale.

Goal: a behavior-driven test suite that (a) pins down how the game *should*
behave, (b) turns each reported bug into a permanent regression test, (c) covers
the core systems deeply, and (d) requires any area shipping content (progs,
custom commands) to bring its own passing tests.

## How tests drive the game

Tests drive the **front door** — `ch.interpret("command string")` — and assert
on captured `ch.send` output plus world state. This exercises the whole real
path: dispatch (prefix-match, `cmd_table`, level/position gating, `Huh?`,
socials) → the ctx shim (`CommandCtx`) → the command's `do_x(ctx)` logic. The
ctx is created by the real shim, exactly as in production; calling `do_x(ctx)`
directly would skip the dispatch layer where several bugs live.

## Harness (`tests/gameplay/helpers.py`)

Built on the existing session-scoped `booted_world` fixture.

- `make_pc(name="Tester", guild="warrior", race="human", room_vnum=ROOM_VNUM_SCHOOL, level=10) -> Pc`
  A real playable `Pc` with an output-capturing `send`. Sets what nanny would
  without the interactive flow: `_race`/race flags, `guild`, `perm_stat`,
  `level`, `position=POS_STANDING`, base group skills, and places it in the room
  instance. Returns the pc; `pc.captured` is the output list.
- `spawn_mob(vnum, room) -> Npc`, `spawn_item(vnum, dest) -> Items` — via
  `object_creator`, placed in a room or an inventory/container.
- `run(pc, command) -> str` — `pc.interpret(command)`, returns text captured
  since the previous `run` (so each assertion sees only that command's output).
- `corpse_in_room(room) -> Items|None`, `item_in(container) -> list` — state
  helpers.

## Phase 1 — bug-first regression (+ fixes)

Each test defines correct behavior; write it red (reproduces the bug), then fix
the code path green.

1. `test_unknown_command_says_huh` — `run(pc, "notacommand")` contains `Huh?`.
2. `test_kill_leaves_corpse` — spawn a mob, `kill` until dead, assert a corpse
   object is in the room (`make_corpse`/`raw_kill` path).
3. `test_look_in_container` — spawn a container item holding an object, `look in
   <container>` lists the contents (do_look "look in" branch).
4. A few neighbors as they surface (e.g. a valid-but-silent command like `list`
   outside a shop should give a clear message, not nothing).

## Phase 2 — full core suite

Deep behavioral tests, grouped by system, each `given/when/then`:
- **Dispatch:** unknown→Huh, social fires, prefix match, abbreviations,
  position gating ("you are sleeping"), level/trust gating.
- **Combat:** hit reduces hp, kill→corpse, corpse holds victim's eq/inv, death
  cry, xp/gain, `is_safe` protects shopkeepers, multi-hit rounds.
- **Objects/containers:** get/put/drop/give, look-in container (open/closed),
  wear/wield/remove, quaff/recite, sacrifice, drink/eat conditions.
- **Movement:** move through exits, closed/locked doors, follow, recall, flee.
- **Shops:** list/buy/sell/value, keeper won't buy junk, gold changes.
- **Spells:** each core spell's primary effect (armor adds AC affect, fireball
  damages, heal restores, cure_* strips, detect_* adds affect, sanctuary, etc.).
- **Skills:** kick/bash/backstab/rescue/disarm land and gate on class/skill.
- **Player lifecycle:** create→save→load round-trip, enter game, score/affects.

Coverage policy: every command in `cmd_table` and every spell in `skill_table`
gets at least a **smoke** assertion (dispatches through `interpret` without a
traceback and without falling to `Huh?` for a real command), on top of the deep
tests.

## Phase 3 — area-content test contract

Any area that ships behavior (a `progs.py`, or custom commands/spells) MUST ship
tests, enforced by the suite:

- Convention: `areas/<name>/tests/test_*.py` (or `areas/<name>/progs_test.py`).
- A contract test `tests/test_area_contract.py` scans `src/areas/*/`: for every
  area with a `progs.py`, assert a corresponding test file exists AND that its
  tests are collected/pass. An area with progs but no tests **fails** the suite
  (like the pyflakes undefined-name guard, but for area content).
- The area's tests use the same harness: spawn the area's mob, fire the trigger
  (speak the keyword, enter the room, give the item), assert the prog's effect.
- Example: `areas/midgaard/tests/test_progs.py` — say "hello" near the wizard
  (vnum 3000) → wizard responds; give it an object → it thanks.

This makes area content self-certifying: a community pack's area can't ship
progs without proving they work against our harness.

## Verification

- `uv run pytest tests` stays green (Phase-1 fixes turn the new red tests green).
- The area-contract test fails if any prog-bearing area lacks passing tests.
- Every future reported gameplay bug lands as a `tests/gameplay/test_*.py` first,
  then a fix.

## Out of scope

- Telnet/nanny e2e beyond the existing smoke (harness enters the game directly).
- Rebalancing or new content — tests assert *stock ROM* behavior.
