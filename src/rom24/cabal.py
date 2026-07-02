"""Cabal kernel: table, lookup, messages, guardian detection, citems ledger.

This module is the ground-truth source for cabal constants used by guardian
progs (Task 6) and future Plan 3b cabal commands.

Ground truth: kbk tables.c:42-55 (CABALS), tables.c:122-134 (MESSAGES),
              kbk merc.h:891-919 (bit letter values), merc.h:1748-1779 (vnums).
"""
from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Guardian act-flag bit values (kbk merc.h:936,953)
#   ACT_INNER_GUARDIAN = (D) = 1<<3 = 8
#   ACT_OUTER_GUARDIAN = (Z) = 1<<25 = 33554432
# In rom24 merc.py: D = 1<<3, Z = 1<<25 — same encoding.
# Verified against entropy.are mob 9901 which carries "ABGLWZde" in its ACT
# field; Z is present confirming it is the outer-guardian bit.
# ---------------------------------------------------------------------------
_ACT_INNER_GUARDIAN = 8          # merc.D
_ACT_OUTER_GUARDIAN = 33554432   # merc.Z  (1 << 25)

# ---------------------------------------------------------------------------
# CABALS — verbatim from kbk tables.c:42-55, ROOM_VNUM_* from merc.h:1748-1761,
# recall vnums from merc.h:1773-1779 (_T suffixed defines).
# Index 0 = none/no-cabal sentinel.
# ---------------------------------------------------------------------------
CABALS: list[dict] = [
    # 0 — none
    {
        "name": "",
        "who_name": "",
        "long_name": "",
        "hall": 3054,        # ROOM_VNUM_ALTAR
        "item_vnum": 1,
        "max_members": 0,
        "recall": 3054,      # ROOM_VNUM_ALTAR
    },
    # 1 — ancient
    {
        "name": "ancient",
        "who_name": "[ANCIENT] ",
        "long_name": "Masters of Intrigue",
        "hall": 3804,        # ROOM_VNUM_ANCIENT
        "item_vnum": 3801,
        "max_members": 50,
        "recall": 3804,      # ROOM_VNUM_ANCIENTT
    },
    # 2 — knight
    {
        "name": "knight",
        "who_name": "[KNIGHT] ",
        "long_name": "Knights of Thera",
        "hall": 4500,        # ROOM_VNUM_KNIGHT
        "item_vnum": 4502,
        "max_members": 50,
        "recall": 4504,      # ROOM_VNUM_KNIGHTT
    },
    # 3 — arcana
    {
        "name": "arcana",
        "who_name": "[ARCANA] ",
        "long_name": "Masters of the Five Magics",
        "hall": 5800,        # ROOM_VNUM_ARCANA
        "item_vnum": 5801,
        "max_members": 50,
        "recall": 5800,      # ROOM_VNUM_ARCANAT
    },
    # 4 — rager
    {
        "name": "rager",
        "who_name": "[RAGER] ",
        "long_name": "Battleragers, Haters of Magic",
        "hall": 5706,        # ROOM_VNUM_RAGER
        "item_vnum": 5701,
        "max_members": 50,
        "recall": 5706,      # ROOM_VNUM_RAGERT
    },
    # 5 — outlaw
    {
        "name": "outlaw",
        "who_name": "[OUTLAW] ",
        "long_name": "Outlaw, Barons of Chaos",
        "hall": 9900,        # ROOM_VNUM_OUTLAW
        "item_vnum": 9902,
        "max_members": 50,
        "recall": 9904,      # ROOM_VNUM_OUTLAWT
    },
    # 6 — empire
    {
        "name": "empire",
        "who_name": "[EMPIRE] ",
        "long_name": "Empire, Subjugator of Nations",
        "hall": 3054,        # ROOM_VNUM_ALTAR (C table uses ALTAR for empire)
        "item_vnum": 8101,
        "max_members": 50,
        "recall": 3054,      # no _T vnum defined; use ALTAR
    },
    # 7 — bounty
    {
        "name": "bounty",
        "who_name": "[BOUNTY] ",
        "long_name": "Bounty Hunters",
        "hall": 3054,        # ROOM_VNUM_ALTAR (C table uses ALTAR for bounty)
        "item_vnum": 8800,
        "max_members": 50,
        "recall": 3054,      # no _T vnum defined; use ALTAR
    },
    # 8 — sylvan
    {
        "name": "sylvan",
        "who_name": "[SYLVAN] ",
        "long_name": "Sylvan Warders of the Glades",
        "hall": 3054,        # ROOM_VNUM_ALTAR (C table uses ALTAR for sylvan)
        "item_vnum": 8900,
        "max_members": 50,
        "recall": 3054,      # no _T vnum defined; use ALTAR
    },
    # 9 — enforcer
    {
        "name": "enforcer",
        "who_name": "[ENFORCER] ",
        "long_name": "Enforcers of Justice",
        "hall": 3054,        # ROOM_VNUM_ALTAR (C table uses ALTAR for enforcer)
        "item_vnum": 4521,
        "max_members": 50,
        "recall": 23603,     # ROOM_VNUM_ENFORCERT
    },
]

# ---------------------------------------------------------------------------
# MESSAGES — verbatim from kbk tables.c:122-134
# Fields: login, logout, entrygreeting
# ---------------------------------------------------------------------------
MESSAGES: list[dict] = [
    # 0 — none
    {"login": "", "logout": "", "entrygreeting": ""},
    # 1 — ancient
    {
        "login": "%s has joined the Hunt.",
        "logout": "%s has left from the Hunt.",
        "entrygreeting": "May the darkness conceal you.",
    },
    # 2 — knight
    {
        "login": "The Code of Honor gleams as %s enters the Castle.",
        "logout": "Farewell %s, the crusades await your return.",
        "entrygreeting": "Greetings, brother Knight.",
    },
    # 3 — arcana
    {
        "login": "The Orb of Magic hums briefly as %s enters the lands.",
        "logout": "The crystal of power dims briefly as %s leaves the lands.",
        "entrygreeting": "Greetings, Master of Magic.",
    },
    # 4 — rager
    {
        "login": "Greetings great warrior of the village!",
        "logout": "Farewell %s. May your strength return to us soon.",
        "entrygreeting": "Welcome, great warrior.",
    },
    # 5 — outlaw
    {
        "login": "The encampment of Outlaws grows as %s enters the realm.",
        "logout": "%s disbands from the outlaw encampments for a while.",
        "entrygreeting": "Greetings, chaotic one.",
    },
    # 6 — empire
    {
        "login": "Imperial power grows as %s enters our realm.",
        "logout": "Our conquest is yet assured though %s leaves us.",
        "entrygreeting": "Greetings, citizen.",
    },
    # 7 — bounty
    {
        "login": "%s has joined the watch.",
        "logout": "%s has left the watch.",
        "entrygreeting": "Hail, Hunter.",
    },
    # 8 — sylvan
    {
        "login": "Welcome, %s, protector of the wilderness.",
        "logout": "The Grove will remain steadfast in your absence, %s.",
        "entrygreeting": "Nature welcomes you.",
    },
    # 9 — enforcer
    {
        "login": "The law grows stronger with the arrival of %s.",
        "logout": "%s signs off from duty and leaves the chaotic streets.",
        "entrygreeting": "Greetings, Enforcer of the Law.",
    },
]


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------

def lookup(name: str) -> int:
    """Prefix-match *name* over CABALS, returning the cabal index (1-9) or 0.

    Mirrors kbk lookup.c:97-108 (cabal_lookup):
      - case-insensitive first-char check, then str_prefix (name is a prefix
        of cabal_table[n].name).
    Index 0 (empty name) is never matched.
    """
    if not name:
        return 0
    name_lower = name.lower()
    for idx, cabal in enumerate(CABALS):
        cabal_name = cabal["name"]
        if not cabal_name:
            continue
        if cabal_name.lower().startswith(name_lower):
            return idx
    return 0


def index_of(value) -> int:
    """Normalise a cabal value to an integer index.

    Accepts:
      - int  → returned as-is (0 passes through unchanged)
      - str  → prefix-matched via lookup(); "" returns 0
      - None → 0
    Used by guardian progs which compare mob.cabal (raw area word) to
    ch.cabal (int) without knowing which side has which type.
    """
    if isinstance(value, int):
        return value
    if not value:
        return 0
    return lookup(str(value))


# ---------------------------------------------------------------------------
# Guardian detection
# ACT_INNER_GUARDIAN = D = 8 (1<<3)    kbk merc.h:936
# ACT_OUTER_GUARDIAN = Z = 33554432    kbk merc.h:953
# ---------------------------------------------------------------------------

def is_inner_guardian(npc) -> bool:
    """True when *npc* carries the ACT_INNER_GUARDIAN bit (D = 8)."""
    return bool(npc.act.is_set(_ACT_INNER_GUARDIAN))


def is_outer_guardian(npc) -> bool:
    """True when *npc* carries the ACT_OUTER_GUARDIAN bit (Z = 33554432)."""
    return bool(npc.act.is_set(_ACT_OUTER_GUARDIAN))


def get_guardian(cabal_idx: int):
    """Return first live NPC with ACT_INNER_GUARDIAN whose cabal matches *cabal_idx*.

    Returns None when no match exists (guardian dead / not yet spawned).
    cabal_idx 0 (none) always returns None.
    """
    if cabal_idx <= 0 or cabal_idx >= len(CABALS):
        return None
    from rom24 import instance
    cabal_name = CABALS[cabal_idx]["name"].lower()
    for npc in instance.npcs.values():
        if not is_inner_guardian(npc):
            continue
        if index_of(npc.cabal) == cabal_idx:
            return npc
    return None


# ---------------------------------------------------------------------------
# Cabal item helpers
# ---------------------------------------------------------------------------
# Pre-built set of valid cabal item vnums (excludes the index-0 placeholder 1).
_CABAL_ITEM_VNUMS: frozenset[int] = frozenset(
    c["item_vnum"] for c in CABALS if c["item_vnum"] > 1
)


def is_cabal_item(item) -> bool:
    """True when *item*'s vnum is one of the ten cabal power items."""
    return item.vnum in _CABAL_ITEM_VNUMS


# ---------------------------------------------------------------------------
# citems ledger  (data/system/citems.txt)
# Format: one "cabal_idx guardian_vnum" pair per line.
# Mirrors kbk sys/citems.txt: pairs until -1 sentinel (we skip the sentinel).
# ---------------------------------------------------------------------------

def _citems_path() -> str:
    """Return the path to citems.txt, reading SYSTEM_DIR at call-time so that
    monkeypatch overrides in tests take effect."""
    from rom24 import settings
    return os.path.join(settings.SYSTEM_DIR, "citems.txt")


def save_items(bindings: list[tuple[int, int]]) -> None:
    """Persist the citems ledger.

    *bindings* is a list of (cabal_idx, guardian_vnum) pairs, where
    guardian_vnum == 0 means "give to the first matching inner guardian".
    """
    path = _citems_path()
    with open(path, "w") as fp:
        for cabal_idx, guardian_vnum in bindings:
            fp.write(f"{cabal_idx} {guardian_vnum}\n")


def load_item_bindings() -> list[tuple[int, int]]:
    """Read the citems ledger and return (cabal_idx, guardian_vnum) pairs.

    Returns an empty list when the file is absent or empty (clean no-op).
    """
    path = _citems_path()
    if not os.path.isfile(path):
        return []
    bindings: list[tuple[int, int]] = []
    with open(path) as fp:
        for line in fp:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            try:
                cabal_idx = int(parts[0])
                guardian_vnum = int(parts[1])
                bindings.append((cabal_idx, guardian_vnum))
            except ValueError:
                logger.warning("load_item_bindings: skipping malformed line %r", line)
    return bindings


def load_items() -> None:
    """Boot-time loader: create cabal item objects and place them on guardians.

    Called by db.boot_db() after all resets have run so guardians are spawned.
    Missing / empty citems.txt is a clean no-op (warns only if a guardian
    referenced in the file cannot be found).
    """
    bindings = load_item_bindings()
    if not bindings:
        return

    # Deferred imports: only needed when there are actual bindings to process.
    from rom24 import instance, object_creator

    for cabal_idx, guardian_vnum in bindings:
        if cabal_idx <= 0 or cabal_idx >= len(CABALS):
            logger.warning("load_items: invalid cabal index %d — skipping", cabal_idx)
            continue

        item_vnum = CABALS[cabal_idx]["item_vnum"]
        if item_vnum not in instance.item_templates:
            logger.warning(
                "load_items: item vnum %d for cabal %d (%s) not in templates — skipping",
                item_vnum, cabal_idx, CABALS[cabal_idx]["name"],
            )
            continue

        item_template = instance.item_templates[item_vnum]

        if guardian_vnum == 0:
            # Give to the matching inner guardian (by cabal flag)
            guardian = get_guardian(cabal_idx)
            if guardian is None:
                logger.warning(
                    "load_items: no inner guardian found for cabal %d (%s) — skipping",
                    cabal_idx, CABALS[cabal_idx]["name"],
                )
                continue
            item = object_creator.create_item(item_template, 0)
            guardian.put(item)
        else:
            # Give to the guardian NPC with the specific vnum
            found = False
            for npc in instance.npcs.values():
                if npc.vnum == guardian_vnum:
                    item = object_creator.create_item(item_template, 0)
                    npc.put(item)
                    found = True
                    break
            if not found:
                logger.warning(
                    "load_items: no mob with vnum %d for cabal %d (%s) — skipping",
                    guardian_vnum, cabal_idx, CABALS[cabal_idx]["name"],
                )
