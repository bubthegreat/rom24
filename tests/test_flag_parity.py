"""Parity guard for flag tables and letter codes.

The JSON-backed flag tables (act_flags, imm_flags, exit_flags, ...) map a flag
name to a bit value. That bit MUST equal the corresponding ``merc`` constant, or
name<->bit conversion silently corrupts data (e.g. a door flag becomes a lock
flag). This test enumerates every merc flag constant per group and asserts the
loaded table carries a matching bit. It fails until every table is complete and
correct against the merc constants.
"""
import pytest

from rom24 import merc, tables, const

# Letter codes A..Z -> bits 0..25, aa..ee -> bits 26..30 (stock ROM range).
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
EXTENDED = ["aa", "bb", "cc", "dd", "ee"]

# Constants intentionally omitted from their JSON table (stock-ROM-consistent).
WHITELIST = {"PLR_OMNI", "AFF_UNUSED_FLAG"}

# (group prefix(es), table object). The table is filled by read_tables at boot.
GROUPS = [
    (("ACT_",), lambda: tables.act_flags),
    (("PLR_",), lambda: tables.plr_flags),
    (("AFF_",), lambda: tables.affect_flags),
    (("OFF_", "ASSIST_"), lambda: tables.off_flags),
    (("IMM_",), lambda: tables.imm_flags),
    (("VULN_",), lambda: tables.vuln_flags),
    (("FORM_",), lambda: tables.form_flags),
    (("PART_",), lambda: tables.part_flags),
    (("COMM_",), lambda: tables.comm_flags),
    (("EX_",), lambda: tables.exit_flags),
    (("WIZ_",), lambda: const.wiznet_table),
]


def _merc_constants(prefixes):
    out = {}
    for name in dir(merc):
        if name in WHITELIST:
            continue
        if any(name.startswith(p) for p in prefixes):
            val = getattr(merc, name)
            if isinstance(val, int):
                out[name] = val
    return out


def test_letter_codes_present_and_correct():
    for i, letter in enumerate(LETTERS):
        assert getattr(merc, letter) == (1 << i), "%s should be 1<<%d" % (letter, i)
    for j, name in enumerate(EXTENDED):
        assert getattr(merc, name) == (1 << (26 + j)), "%s should be 1<<%d" % (name, 26 + j)


def test_flag_tables_cover_all_merc_constants(booted_world):
    missing = []
    for prefixes, get_table in GROUPS:
        table = get_table()
        table_bits = {entry.bit for entry in table.values()}
        for name, val in _merc_constants(prefixes).items():
            if val not in table_bits:
                missing.append((name, val, prefixes[0], sorted(table_bits)))
    assert not missing, "flag table(s) missing/incorrect bits:\n" + "\n".join(
        "  %s=%d not in %s table (has %s)" % (n, v, p, bits) for n, v, p, bits in missing
    )
