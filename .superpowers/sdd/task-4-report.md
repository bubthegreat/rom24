# Task 4: Emit `content/skills.py` and `content/groups.py` — Report

## Status
✅ **COMPLETE** — All requirements met, tests pass, type checking passes.

## Implementation Summary
Implemented three functions in `tools/kbk_import/emit.py`:

1. **`_per_class(values, r, order)`** — Helper function that builds per-class dictionaries by mapping class names (from `order`) to resolved numeric values using `r.num()`. Handles variable-length input gracefully with index-based filtering.

2. **`emit_skills(entries, r, class_order)`** — Emits `skills.py` module defining `SKILLS: dict[str, dict]` with all 14 required keys:
   - Per-class fields: `skill_level`, `rating` (built via `_per_class()`)
   - Resolved scalar fields: `target`, `minimum_position`, `min_mana`, `beats`, `ctype`
   - Resolved special fields: `spell_fun` (via `r.spell_name()`), `pgsn` (via `r.gsn_name()`), `slot` (via `r.slot()`)
   - String fields: `name`, `noun_damage`, `msg_off`, `msg_obj`
   - Filtering: skips entries with empty or "reserved" names

3. **`emit_groups(entries, r, class_order)`** — Emits `groups.py` module defining `GROUPS: dict[str, dict]` with all 3 required keys:
   - Per-class field: `rating` (built via `_per_class()`)
   - String field: `name`
   - List field: `spells` (filtered to exclude empty values via conditional list comprehension)
   - Filtering: skips entries with empty names

## Test Results
Created `tests/kbk_import/test_emit_skills.py` with comprehensive test coverage:

- **`test_emit_skills()`** — Validates skills module generation:
  - ✅ Filtered out "reserved" entries
  - ✅ Per-class dicts correctly mapped: `{"warrior": 53, "thief": 33}`
  - ✅ Spell function name extracted from C function: `"acid blast"`
  - ✅ GSN name extracted: `"acid"`
  - ✅ All numeric fields resolved correctly

- **`test_emit_groups()`** — Validates groups module generation:
  - ✅ Per-class rating dict correctly built: `{"warrior": 1, "thief": 3}`
  - ✅ Spell list correctly parsed and filtered

All 15 tests in `tests/kbk_import/` pass. Type checking (`uv run ty check`) passes with no errors.

## Commit
**Hash:** `63f1c1ae62295989123848851d2f5d67ada2d10c`
**Message:** `feat(kbk-import): emit skills + groups modules`

## Code Quality Notes
- Emission is deterministic: uses insertion-ordered dicts throughout (Python 3.7+ guarantees dict insertion order)
- No `set` iteration that could leak into output
- Follows established patterns from `emit_classes()` (same structure, header, and formatting)
- All Resolver methods used correctly: `.num()`, `.value()`, `.slot()`, `.gsn_name()`, `.spell_name()`
- Field order in self-review checklist verified:
  - **SKILLS**: name, skill_level, rating, spell_fun, target, minimum_position, pgsn, slot, min_mana, beats, noun_damage, msg_off, msg_obj, ctype ✅
  - **GROUPS**: name, rating, spells ✅
- Reserved and empty-name entries correctly excluded ✅

## Concerns
None. Task requirements fully satisfied, all tests pass, type safety maintained.

---

## Code Review Fixes Applied

### Changes Made
Three targeted fixes to handle real-world data edge cases in the kbk const.c source:

1. **emit_skills() bounds-guarding** (tools/kbk_import/emit.py, lines 70-71)
   - Problem: 6 of 640 skill entries in const.c have only 13 fields (missing `ctype` at index 13)
   - Fix: Guard `msg_obj` and `ctype` field access with length checks:
     - `"msg_obj": r.value(e[12]) if len(e) > 12 else ""`
     - `"ctype": r.num(e[13]) if len(e) > 13 else 0`
   - Result: Gracefully defaults missing trailing fields (C zero-initialization semantics)

2. **emit_groups() reserved filtering** (tools/kbk_import/emit.py, line 80)
   - Problem: `emit_groups()` was not filtering "reserved" entries (inconsistent with `emit_skills()`)
   - Fix: Changed condition from `if not name:` to `if not name or name == "reserved":`
   - Result: Consistent filtering behavior across both emitters

3. **resolve.py slot() robustness** (tools/kbk_import/resolve.py, lines 38-50)
   - Problem: Real data contains two edge cases:
     - Entry "outfit": bare numeric `0` instead of `SLOT(0)`
     - Entry "aura": typo `SLOT(O)` (capital O) instead of `SLOT(0)`
   - Fix: Enhanced `slot()` to:
     - Replace `SLOT(O)` → `SLOT(0)` (typo correction)
     - Fall back to bare numeric parsing if `SLOT(N)` regex fails
   - Result: Handles both spec-compliant and real-world malformed values

### Test Coverage
Added `test_emit_skills_tolerates_truncated_entries()` to tests/kbk_import/test_emit_skills.py:
- Tests skill with 13 fields (no ctype): validates `msg_obj=""` and `ctype==0` defaults
- Verifies round-trip: parse → emit → exec → validate

### Verification Against Real Data
End-to-end validation command executed successfully:
```
uv run python -c "
from tools.kbk_import import cparse, emit
from tools.kbk_import.resolve import Resolver
src = open('/home/bub/Development/kbk/src/const.c', encoding='latin-1').read()
merc = open('/home/bub/Development/kbk/src/merc.h', encoding='latin-1').read()
defines = {**cparse.parse_defines(merc), **cparse.parse_defines(src)}
r = Resolver(defines)
t = lambda n: cparse.parse_braces(cparse.extract_initializer(src, n))
csrc, order = emit.emit_classes(t('class_table'), r)
ns = {}; exec(emit.emit_skills(t('skill_table'), r, order), ns)
ns2 = {}; exec(emit.emit_groups(t('group_table'), r, order), ns2)
print('skills:', len(ns['SKILLS']), 'groups:', len(ns2['GROUPS']))
"
```
**Output:** `skills: 636 groups: 35` ✅

### Test Results
- **pytest:** `tests/kbk_import/` → 16 passed ✅
- **type check:** `uv run ty check tools/ tests/kbk_import/` → All checks passed ✅

### Commit
**Hash:** `0fb3660`
**Message:** `fix(kbk-import): tolerate truncated C skill entries; filter reserved groups`

---

## Review-Mandated Fixes Applied

### Coordinator Decisions
1. **SLOT values follow COMPILED C TRUTH**: Define constants resolve to their C values, so `SLOT(O)` → `16384` because `merc.h` defines `O=16384`
2. **Duplicate skill names use FIRST-WINS**: Matches C `skill_lookup()` behavior of returning the first match

### Changes Made

1. **tools/kbk_import/resolve.py** — Rewrote `slot()` method
   - **Before:** Hard-coded string substitution (`SLOT(O)` → `SLOT(0)`) and bare-int fallback
   - **After:** Extracts `SLOT(expr)` and resolves expr via `num()`, allowing any define:
     ```python
     def slot(self, token: str) -> int:
         tok = str(token).strip()
         m = re.fullmatch(r"SLOT\s*\((.*)\)", tok)
         return self.num((m.group(1) if m else tok).strip())
     ```
   - Result: `SLOT(O)` now correctly resolves to 16384 when `O=16384` is defined

2. **tools/kbk_import/emit.py** — Added first-wins duplicate handling in `emit_skills()`
   - After extracting skill name and before adding to dict, skip if name already exists:
     ```python
     if name in skills:
         continue  # duplicate names: C skill_lookup returns the first match
     ```
   - Result: Multiple skill definitions with the same name only keep the first entry

3. **tests/kbk_import/test_resolve.py** — Added `test_slot_variants()` test
   - Updated defines dict to include `"O": "16384"`
   - Tests coverage:
     - ✅ `r.slot("SLOT(70)")` == 70
     - ✅ `r.slot("SLOT(O)")` == 16384 (define resolution)
     - ✅ `r.slot("SLOT( O )")` == 16384 (whitespace handling)
     - ✅ `r.slot("0")` == 0 (fallback to bare int)
     - ✅ `r.slot("SLOT(garbage)")` raises ValueError (error handling)

4. **tests/kbk_import/test_emit_skills.py** — Added `test_emit_skills_duplicate_names_first_wins()` test
   - Tests duplicate skill entries with same name ("beast call")
   - Verifies first entry is kept: `min_mana==50` (from first), not 0 (from second)
   - Verifies spell_fun is correctly extracted: `"beast call"` (from first entry's spell function)

### Verification Against Real Data
Executed real-data validation command:
```
uv run python -c "
from tools.kbk_import import cparse, emit
from tools.kbk_import.resolve import Resolver
src = open('/home/bub/Development/kbk/src/const.c', encoding='latin-1').read()
merc = open('/home/bub/Development/kbk/src/merc.h', encoding='latin-1').read()
r = Resolver({**cparse.parse_defines(merc), **cparse.parse_defines(src)})
t = lambda n: cparse.parse_braces(cparse.extract_initializer(src, n))
_, order = emit.emit_classes(t('class_table'), r)
ns = {}; exec(emit.emit_skills(t('skill_table'), r, order), ns)
print('aura slot:', ns['SKILLS']['aura']['slot'])
print('beast call mana/fun:', ns['SKILLS']['beast call']['min_mana'], ns['SKILLS']['beast call']['spell_fun'])
print('total:', len(ns['SKILLS']))
"
```

**Output:**
```
aura slot: 16384
beast call mana/fun: 50 beast call
total: 636
```
✅ All values match expectations

### Test Results
- **pytest:** `tests/kbk_import/` → **18 passed** ✅
- **type check:** `uv run ty check tools/ tests/kbk_import/` → **All checks passed** ✅

### Commit
**Hash:** `3e43f1c`
**Message:** `fix(kbk-import): slot() resolves defines (compiled C truth); first-wins duplicate skills`

---

## Final Review Fix: Zero-Fill Per-Class Arrays

### Problem Identified
The `_per_class()` function was only including classes that had corresponding values in the input array. However, C zero-initializes missing trailing array elements, so all classes in `order` must appear in the output, defaulting to 0 when no value is present.

**Example:** If ORDER = ["warrior", "thief"] and a skill has only `{53}` for skill_level, the output should be `{"warrior": 53, "thief": 0}`, not just `{"warrior": 53}`.

### Changes Made

1. **tools/kbk_import/emit.py** — Rewrote `_per_class()` helper function (lines 47-48)
   - **Before:** `{order[i]: r.num(v) for i, v in enumerate(values) if i < len(order)}`
   - **After:** `{cls: r.num(values[i]) if i < len(values) else 0 for i, cls in enumerate(order)}`
   - **Rationale:** Iterate through `order` (the list of classes), and for each class at index i, resolve the value at `values[i]` if it exists, otherwise default to 0
   - Result: All classes in the order appear in the output dict, matching C's zero-initialization semantics

2. **tests/kbk_import/test_emit_skills.py** — Added `test_per_class_zero_fills_short_arrays()` test
   - Tests skill with truncated per-class arrays: `{53}` for skill_level and `{1}` for rating
   - Verifies correct zero-filling: 
     - `skill_level` → `{"warrior": 53, "thief": 0}`
     - `rating` → `{"warrior": 1, "thief": 0}`

3. **tests/kbk_import/test_emit_skills.py** — Cleanup: Removed unused self-referential entry
   - Removed `"spell_beast_call": "spell_beast_call"` from DEFS dict (was never used by any test)

### Verification

**Unit Tests:** `uv run pytest tests/kbk_import/ -q`
```
============================== 19 passed in 0.11s ==============================
```
✅ All 19 tests pass (includes new zero-fill test)

**Type Checking:** `uv run ty check tools/ tests/kbk_import/`
```
All checks passed!
```
✅ Type safety maintained

**Real-Data Validation:** Confirmed against `/home/bub/Development/kbk/src/const.c`
```
uv run python -c "
from tools.kbk_import import cparse, emit
from tools.kbk_import.resolve import Resolver
src = open('/home/bub/Development/kbk/src/const.c', encoding='latin-1').read()
merc = open('/home/bub/Development/kbk/src/merc.h', encoding='latin-1').read()
r = Resolver({**cparse.parse_defines(merc), **cparse.parse_defines(src)})
t = lambda n: cparse.parse_braces(cparse.extract_initializer(src, n))
_, order = emit.emit_classes(t('class_table'), r)
ns = {}; exec(emit.emit_skills(t('skill_table'), r, order), ns)
gs = {}; exec(emit.emit_groups(t('group_table'), r, order), gs)
print('haggle healer:', ns['SKILLS']['haggle']['skill_level']['healer'])
print('hunter rating keys:', len(gs['GROUPS']['hunter']['rating']))
"
```

**Output:**
```
haggle healer: 0
hunter rating keys: 13
```
✅ haggle's healer class defaults to 0 (was truncated in source)
✅ hunter group has all 13 classes in rating dict (zero-filled as needed)

### Commit
**Hash:** (pending)
**Message:** `fix(kbk-import): zero-fill short per-class arrays (C zero-init truth)`

### Impact
- **Skills:** All 636 skills now guarantee all classes appear in `skill_level` and `rating` dicts
- **Groups:** All 35 groups now guarantee all classes appear in `rating` dict
- **Semantics:** Output now precisely matches C's zero-initialization of array elements
- **Backward Compatibility:** Existing full-length arrays work identically; only truncated arrays get filled
