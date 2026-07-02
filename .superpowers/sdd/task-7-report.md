# Task 7 Report: Spell Stubs — Cast Path

## Gate Change (Before / After)

### Before

```python
if (
    not sn
    or sn.spell_fun is None
    or (
        not ch.is_npc()
        and (
            ch.level < sn.skill_level[ch.guild.name]
            or ch.learned.get(sn.name, 0) == 0
        )
    )
):
    ch.send("You don't know any spells of that name.\n")
    return
```

The `sn.spell_fun is None` arm was co-mingled with "spell not found" and
"character hasn't learned it" — all three routes hit "You don't know any spells
of that name." This meant every one of the ~230 KBK stub spells (spell_fun=None)
was unreachable to a player who actually knew it.

### After

```python
if not sn or (
    not ch.is_npc()
    and (
        ch.level < sn.skill_level[ch.guild.name]
        or ch.learned.get(sn.name, 0) == 0
    )
):
    ch.send("You don't know any spells of that name.\n")
    return
```

`sn.spell_fun is None` is removed from this gate entirely.  A stub spell
that exists in the skill_table (sn is not None) and whose level/learned checks
pass now flows through.  The NPC path (skips the inner condition) is unchanged.

## Stub Placement Rationale

Two new module-level items were added before `do_cast`:

```python
STUB_MSG = "You trace the pattern, but nothing happens - that magic has not been rewoven yet.\n"

def spell_is_castable_stub(sn):
    """Return True if sn is a known-but-unimplemented (KBK) spell stub."""
    return sn is not None and sn.spell_fun is None
```

Inside `do_cast`, the intercept point is immediately before the mana-availability
check:

```python
# After target resolution, BEFORE mana deduction / lag:
if spell_is_castable_stub(sn):
    ch.send(STUB_MSG)
    return
```

**Why this position is correct:**

- Target resolution runs first, so offensive stub spells that need a target will
  still request one ("Cast the spell on whom?") before the stub fires — intentional:
  the player picked a spell that needs a target, so the request is valid.  If target
  resolution itself fails early (victim not found, etc.), those early returns fire
  first, keeping the stub path unreachable for malformed input.
- Mana deduction: `ch.mana -= mana // 2` (on skill-roll failure) and
  `ch.mana -= mana` (on success) are both inside the `say_spell / WAIT_STATE /
  random.randint` block that comes AFTER the intercept point — no mana is ever spent.
- WAIT_STATE (lag): `state_checks.WAIT_STATE(ch, sn.beats)` is in the same
  post-intercept block — no lag is applied.
- `say_spell` (echo to room): also post-intercept — the room does not hear the
  incantation.
- `check_improve` / combat counter-attack: post-intercept — neither fires.

The `minimum_position` check runs before the intercept point and has no side-effects,
producing its own early return ("You can't concentrate enough.").  The mana
*availability* check (`ch.mana < mana`) runs after the intercept point — the stub
returns before it runs.  Both are harmless for stub spells.

## obj_cast_spell Guard Verification

`handler_magic.obj_cast_spell` already guards stub spells at line 158:

```python
if sn not in const.skill_table or not const.skill_table[sn].spell_fun:
    print("BUG: Obj_cast_spell: bad sn %d." % sn)
    return
```

This guard is correct for the object-casting context (data condition, not player
action) and cannot crash — it returns before ever dereferencing spell_fun.
Left as-is per brief.

## Coverage Statement

Full integration testing (a character object with guild, learned map, mana, room,
etc. wired up and `do_cast` called end-to-end) is not feasible in unit tests —
the full character state machine requires a live game loop (confirmed by Task 6
investigation).  Coverage provided:

- `test_stub_spell_castable_shape` — verifies "banshee call" has spell_fun=None
  and that `spell_is_castable_stub` returns True for it (the brief's floor test).
- `test_stub_helper_returns_false_for_implemented_spell` — verifies the helper
  does NOT mark a real spell (acid blast) as a stub.
- `test_stub_helper_returns_false_for_none` — verifies None sn is not treated
  as a stub (guards the `sn is not None` branch of the helper).
- `test_gate_condition_allows_stub_through` — structural test verifying the
  separation: a stub sn is non-None (passes `not sn` gate) and spell_fun is
  None (caught only by the helper, not the gate).

The end-to-end path (player types `cast banshee call`, message arrives, no mana
deducted, no lag applied) is deferred to Task 10's manual telnet smoke test.

## Files Modified

- `src/rom24/commands/do_cast.py` — gate split, STUB_MSG + spell_is_castable_stub
  helper added, stub intercept inserted before mana deduction
- `tests/test_spell_stub.py` — new test file (4 tests)
- `.superpowers/sdd/task-7-report.md` — this report

## Post-Review Fix (2026-07-02)

Applied code-review findings:

1. **Critical**: Guarded both `fight.check_killer(ch, victim)` call sites
   (TAR_CHAR_OFFENSIVE ~line 78, TAR_OBJ_CHAR_OFF ~line 131) with
   `if not spell_is_castable_stub(sn)` check to prevent PK state mutation
   (PLR_KILLER flag, wiznet broadcast) on offensive stub spells.

2. **Important**: Added `test_stub_msg_exact_text` test to pin the STUB_MSG
   literal text ("You trace the pattern...") in tests/test_spell_stub.py.

3. **Minor**: Corrected flow description: mana availability check
   (`ch.mana < mana`) runs AFTER the stub intercept (~line 166), not before —
   stub returns at line 164 before mana check is evaluated.

All 56 tests pass; type checking clean. Commit: c91373a.
