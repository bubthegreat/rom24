# Command/Spell ctx-API — Design Spec (Pilot)

Date: 2026-08-11
Status: Approved (brainstorm) — pilot phase

## Context

Commands (213) and spells (96) now live in `packs/core` and load by file path.
They reach into ~20 engine modules via deep imports (`from rom24 import merc,
fight, handler_game, state_checks, instance, const, game_utils, …`). That wide,
unofficial surface is fragile: any engine refactor can break community content,
and a pack author must learn 20 modules.

Goal: a stable, curated API so command/spell/prog authors write against one
documented surface with guardrails. Chosen shape: a **ctx-style handle** (like
the prog `Ctx`), adopted incrementally, starting with a **pilot** of a few
commands + spells to prove the ergonomics before any broad rollout.

## Decisions (locked in brainstorm)

1. **Shape:** ctx-style handle. A command becomes `def do_x(ctx): …`; behavior
   goes through `ctx` methods, not deep imports.
2. **Migration:** pilot a few, then decide. Build the API + decorator, convert a
   representative set, validate live, then choose big-bang vs incremental.
3. **Coexistence:** old `(ch, argument)` commands keep working unchanged; both
   styles register into the same `cmd_table` and dispatch identically.

## Components

### `rom24.api` — the stable surface

The only module a command/spell file imports. Provides:
- **Decorators:** `@api.command(name, *, pos, level=0, log=merc.LOG_NORMAL,
  show=1, aliases=())`, `@api.spell(name, *, target, min_pos, min_mana, beats,
  lag)` (spell metadata mirrors the current `skill_type`).
- **Constants:** re-exports `merc` public names (`api.POS_FIGHTING`,
  `api.TO_ROOM`, `api.DAM_BASH`, …) plus `api.merc` for the full set.
- **Registration under the hood:** wraps the `func(ctx)` in a shim and calls the
  existing `interp.register_command` / `const.register_spell`.

### `CommandCtx` — per-call handle

Built by the command shim from `(ch, argument)`.
- State: `ctx.ch`, `ctx.arg`, `ctx.room`, `ctx.fighting`
- Args: `ctx.word()` (pop next word, mutating `ctx.arg`), `ctx.rest`
- Output: `ctx.send(text)`, `ctx.act(fmt, to=api.TO_ROOM, arg1=None, arg2=None)`,
  `ctx.to_char(fmt, …)`, `ctx.to_room(fmt, …)`
- Lookup: `ctx.char_in_room(name)`, `ctx.char_world(name)`,
  `ctx.obj_in_room(name)`, `ctx.obj_carried(name)`, `ctx.mob_proto(vnum)`,
  `ctx.obj_proto(vnum)`, `ctx.room_at(vnum)`
- Combat: `ctx.damage(victim, amount, dt=api.TYPE_UNDEFINED,
  dam_type=api.DAM_NONE)`, `ctx.multi_hit(victim)`, `ctx.kill(victim)`,
  `ctx.is_safe(victim)`
- Skills: `ctx.cast(spell, target=None)`, `ctx.skill(name)` (learned %)
- Util: `ctx.rand(a, b)`, `ctx.dice(n, s)`, `ctx.wait(pulses)`
- **Escape hatch:** `ctx.engine` — a namespace exposing the raw engine modules
  (`ctx.engine.fight`, `ctx.engine.handler_game`, `ctx.engine.instance`, …),
  documented as **unstable**. Lets a command adopt `ctx` for what is wrapped and
  drop to `ctx.engine.foo` for the rest, so migration never blocks.

### `SpellCtx`

Built from `(sn, level, ch, vo, target)`. Adds `ctx.sn`, `ctx.level`,
`ctx.target` (vo), `ctx.target_type`; shares the output/combat/util/lookup
helpers with `CommandCtx` (common base class `BaseCtx`).

### Registration + coexistence

`@api.command`:
1. define `shim(ch, argument)`: build `CommandCtx(ch, argument)`, call `func(ctx)`.
2. `shim.__name__ = func.__name__` — so `setattr(Living, do_fun.__name__, shim)`
   in `cmd_type.__init__` binds `ch.do_x` correctly (fight/progs call this).
3. `interp.register_command(interp.cmd_type(name, shim, pos, level, log, show))`
   and one registration per alias.

`@api.spell` registers a `spell_fun(sn, level, ch, vo, target)` shim via
`const.register_spell` with the given metadata.

Old-style files calling `interp.register_command(interp.cmd_type(...))` directly
are untouched. `cmd_table`, `Living` binding, and `spell_fun` dispatch are
identical for both.

## Pilot scope

Convert to ctx-style (representative spread: output, combat, movement, objects,
spells):
- Commands: `do_say`, `do_kick`, `do_look`, `do_get`, `do_bash`
- Spells: `spell_armor`, `spell_fireball`

Everything else stays old-style.

## Guardrails

- `ctx` methods are the stable contract; `ctx.engine` is explicitly unstable.
- Same exception isolation philosophy as progs for author code where it applies.
- The prog `Ctx` (already shipped) and these ctxs share concepts; a later step
  can unify them on `BaseCtx`.

## Verification

- Unit tests: each piloted command/spell dispatched through `cmd_table` /
  `skill_table` produces the expected effect (uses the `command` conftest
  fixture).
- Live: telnet session — create a char, run say/look/get/kick/bash, cast
  armor + fireball — observe correct behavior.
- Full suite stays green (currently 52).

## Out of scope (pilot)

- Converting the other ~300 files (decision deferred to after the pilot).
- Unifying prog `Ctx` with `BaseCtx` (later).
- Constant curation (re-export `merc` wholesale for now).
