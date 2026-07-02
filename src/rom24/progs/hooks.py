"""Prog hook helpers for movement and speech dispatch sites.

These helpers encapsulate the exact C ordering from act_move.c and act_comm.c so
that each call site adds a single function call rather than inline loops.

Design decisions
----------------
Room entry_prog lives in Room.put() (handler_room.py) so it fires on *every*
char-to-room transition: normal movement, login, teleport, recall.  The
fire_arrival helper covers the movement-specific cluster (greet/entry progs
for chars and objects already/newly in the room).

fire_pre_move is called *before* Room.get/put (movement still cancellable).
fire_arrival is called *after* Room.put (ch is in the new room).
fire_speech is called from do_say after the existing pyprogs signal.
"""

import logging

logger = logging.getLogger(__name__)

from rom24 import instance
from rom24.progs import dispatch


# ---------------------------------------------------------------------------
# Pre-move hook (C act_move.c:294)
# ---------------------------------------------------------------------------

def fire_pre_move(ch, door):
    """Fire move_progs for every NPC currently in ch's room.

    Args:
        ch:   The character about to move.
        door: Direction integer (0-5).

    Returns:
        True if any NPC's move_prog vetoed the movement (blocked it).
    """
    room = ch.in_room
    if room is None:
        return False
    for npc_id in room.people[:]:
        npc = instance.characters.get(npc_id)
        if npc is None or npc is ch:
            continue
        if npc.is_npc():
            if dispatch.fire(npc, "move_prog", ch, room, door):
                return True
    return False


# ---------------------------------------------------------------------------
# Post-arrival hook (C act_move.c:486-534)
# ---------------------------------------------------------------------------

def fire_arrival(ch):
    """Fire the post-arrival prog cluster after ch has entered a new room.

    Does NOT fire the room entry_prog — that belongs in Room.put() so that
    teleport/login/recall also trigger it.  This helper fires:

    1. greet_prog on items carried by chars already in the room (C :486).
    2. greet_prog on mobs already in the room, only if the room has a PC (C :493).
    3. entry_prog on each item ch is carrying (C :498).
    4. entry_prog on ch itself if ch is an NPC (C :507).

    Args:
        ch: The character that just arrived (already placed in the room).
    """
    room = ch.in_room
    if room is None:
        return

    # Determine if the room has any PC (including the arriving char).
    has_pc = any(
        not instance.characters[cid].is_npc()
        for cid in room.people
        if cid in instance.characters
    )

    for cid in room.people[:]:
        if cid == ch.instance_id:
            continue
        other = instance.characters.get(cid)
        if other is None:
            continue

        # (1) Items carried by chars already in the room: greet_prog(obj, ch)
        for item_id in other.items:
            item = instance.items.get(item_id)
            if item is not None:
                dispatch.fire(item, "greet_prog", ch)

        # (2) Mob greet_prog(mob, ch) — only when room contains a PC
        if other.is_npc() and has_pc:
            dispatch.fire(other, "greet_prog", ch)

    # (3) ch's carried items: entry_prog(obj)
    for item_id in ch.items:
        item = instance.items.get(item_id)
        if item is not None:
            dispatch.fire(item, "entry_prog")

    # (4) ch is an NPC with entry_prog: fire entry_prog(ch)
    if ch.is_npc():
        dispatch.fire(ch, "entry_prog")


# ---------------------------------------------------------------------------
# Speech hook (C act_comm.c:930-950)
# ---------------------------------------------------------------------------

def fire_speech(ch, text):
    """Fire speech progs after ch speaks in a room.

    Order (C act_comm.c:930-950):
    (a) Mobs in room (not the speaker): speech_prog(mob, ch, text)
    (b) Items in room contents: speech_prog(obj, ch, text)
    (c) Items carried by everyone in the room: speech_prog(obj, ch, text)
    (d) Room itself: speech_prog(room, ch, text)

    Args:
        ch:   The speaking character.
        text: The spoken string.
    """
    room = ch.in_room
    if room is None:
        return

    # (a) Mobs in room (not the speaker)
    for cid in room.people[:]:
        if cid == ch.instance_id:
            continue
        mob = instance.characters.get(cid)
        if mob is not None and mob.is_npc():
            dispatch.fire(mob, "speech_prog", ch, text)

    # (b) Items in room
    for item_id in room.items:
        item = instance.items.get(item_id)
        if item is not None:
            dispatch.fire(item, "speech_prog", ch, text)

    # (c) Items carried by everyone in the room (including the speaker)
    for cid in room.people[:]:
        person = instance.characters.get(cid)
        if person is None:
            continue
        for item_id in person.items:
            item = instance.items.get(item_id)
            if item is not None:
                dispatch.fire(item, "speech_prog", ch, text)

    # (d) Room speech_prog
    dispatch.fire(room, "speech_prog", ch, text)
