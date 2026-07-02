"""Unit tests for progs/hooks.py dispatch helpers.

Coverage strategy
-----------------
All three helpers (fire_pre_move, fire_arrival, fire_speech) are tested with
minimal fake objects that mirror the real attribute interfaces:
  - room.people / room.items  (Inventory properties — replicated as tuples)
  - ch.items                  (Inventory.items property — replicated as tuple)
  - instance.characters / instance.items patched via mock.patch.dict

Integration with move_char / Room.put / do_say is exercised by the existing
boot suite (test_boot_kbk) which must pass without errors after the wiring;
full live-walk acceptance is deferred to Task 8 per the plan.
"""
import types
import unittest.mock as mock
import pytest

import rom24.instance as _instance
from rom24.progs import hooks, dispatch


# ---------------------------------------------------------------------------
# Fake object helpers
# ---------------------------------------------------------------------------

_next_id = 10_000


def _next():
    global _next_id
    _next_id += 1
    return _next_id


class FakeRoom:
    """Minimal room-like object."""
    def __init__(self, people_ids=(), item_ids=()):
        self.instance_id = _next()
        self._people = tuple(people_ids)
        self._items = tuple(item_ids)
        self.progs = {}

    @property
    def people(self):
        return self._people

    @property
    def items(self):
        return self._items


class FakeChar:
    """Minimal character-like object."""
    def __init__(self, npc=False, item_ids=(), room=None):
        self.instance_id = _next()
        self._is_npc = npc
        self._item_ids = tuple(item_ids)
        self._room = room
        self.progs = {}

    def is_npc(self):
        return self._is_npc

    @property
    def in_room(self):
        return self._room

    @property
    def items(self):
        return self._item_ids


class FakeItem:
    """Minimal item-like object."""
    def __init__(self):
        self.instance_id = _next()
        self.progs = {}


# ---------------------------------------------------------------------------
# Context manager: patch instance dicts with local fakes
# ---------------------------------------------------------------------------

def _patch_instance(chars=None, items=None):
    """Return a context stack that replaces instance.characters / instance.items."""
    chars = chars or {}
    items = items or {}
    return mock.patch.multiple(
        "rom24.instance",
        characters=chars,
        items=items,
    )


# ---------------------------------------------------------------------------
# fire_pre_move tests
# ---------------------------------------------------------------------------

class TestFirePreMove:
    def test_no_npcs_returns_false(self):
        pc = FakeChar(npc=False)
        room = FakeRoom(people_ids=(pc.instance_id,))
        pc._room = room
        with _patch_instance(chars={pc.instance_id: pc}):
            assert hooks.fire_pre_move(pc, 0) is False

    def test_npc_without_move_prog_returns_false(self):
        mover = FakeChar(npc=False)
        npc = FakeChar(npc=True)
        room = FakeRoom(people_ids=(mover.instance_id, npc.instance_id))
        mover._room = room
        npc._room = room
        with _patch_instance(chars={mover.instance_id: mover, npc.instance_id: npc}):
            assert hooks.fire_pre_move(mover, 0) is False

    def test_npc_move_prog_veto_returns_true(self):
        mover = FakeChar(npc=False)
        npc = FakeChar(npc=True)
        npc.progs = {"move_prog": [lambda ch, room, door: False]}  # C: False = block
        room = FakeRoom(people_ids=(mover.instance_id, npc.instance_id))
        mover._room = room
        npc._room = room
        with _patch_instance(chars={mover.instance_id: mover, npc.instance_id: npc}):
            assert hooks.fire_pre_move(mover, 0) is True

    def test_npc_move_prog_allow_returns_false(self):
        mover = FakeChar(npc=False)
        npc = FakeChar(npc=True)
        npc.progs = {"move_prog": [lambda ch, room, door: None]}  # None = allow
        room = FakeRoom(people_ids=(mover.instance_id, npc.instance_id))
        mover._room = room
        npc._room = room
        with _patch_instance(chars={mover.instance_id: mover, npc.instance_id: npc}):
            assert hooks.fire_pre_move(mover, 0) is False

    def test_skips_self_in_room(self):
        """NPC moving through a room containing itself must not self-veto."""
        npc = FakeChar(npc=True)
        npc.progs = {"move_prog": [lambda ch, room, door: False]}
        room = FakeRoom(people_ids=(npc.instance_id,))
        npc._room = room
        with _patch_instance(chars={npc.instance_id: npc}):
            assert hooks.fire_pre_move(npc, 1) is False

    def test_no_room_returns_false(self):
        ch = FakeChar(npc=False)
        ch._room = None
        with _patch_instance():
            assert hooks.fire_pre_move(ch, 0) is False

    def test_door_passed_to_prog(self):
        mover = FakeChar(npc=False)
        npc = FakeChar(npc=True)
        seen = []
        npc.progs = {"move_prog": [lambda ch, room, door: seen.append(door)]}
        room = FakeRoom(people_ids=(mover.instance_id, npc.instance_id))
        mover._room = room
        npc._room = room
        with _patch_instance(chars={mover.instance_id: mover, npc.instance_id: npc}):
            hooks.fire_pre_move(mover, 3)
        assert seen == [3]


# ---------------------------------------------------------------------------
# fire_arrival tests
# ---------------------------------------------------------------------------

class TestFireArrival:
    def test_greet_prog_on_carried_item_fires(self):
        item = FakeItem()
        item.progs = {"greet_prog": []}
        seen = []
        item.progs["greet_prog"].append(lambda ch: seen.append(ch))

        resident = FakeChar(npc=False, item_ids=(item.instance_id,))
        mover = FakeChar(npc=False)
        room = FakeRoom(people_ids=(resident.instance_id, mover.instance_id))
        mover._room = room

        with _patch_instance(
            chars={resident.instance_id: resident, mover.instance_id: mover},
            items={item.instance_id: item},
        ):
            hooks.fire_arrival(mover)

        assert seen == [mover]

    def test_mob_greet_prog_fires_when_pc_present(self):
        seen = []
        mob = FakeChar(npc=True)
        mob.progs = {"greet_prog": [lambda ch: seen.append(ch)]}
        pc = FakeChar(npc=False)           # the mover (a PC)
        room = FakeRoom(people_ids=(mob.instance_id, pc.instance_id))
        pc._room = room

        with _patch_instance(chars={mob.instance_id: mob, pc.instance_id: pc}):
            hooks.fire_arrival(pc)

        assert seen == [pc]

    def test_mob_greet_prog_does_not_fire_when_no_pc(self):
        seen = []
        mob1 = FakeChar(npc=True)
        mob1.progs = {"greet_prog": [lambda ch: seen.append(ch)]}
        mover_npc = FakeChar(npc=True)      # mover is also an NPC
        room = FakeRoom(people_ids=(mob1.instance_id, mover_npc.instance_id))
        mover_npc._room = room

        with _patch_instance(chars={mob1.instance_id: mob1, mover_npc.instance_id: mover_npc}):
            hooks.fire_arrival(mover_npc)

        assert seen == []

    def test_npc_mover_entry_prog_fires(self):
        seen = []
        npc = FakeChar(npc=True)
        npc.progs = {"entry_prog": [lambda: seen.append("fired")]}
        room = FakeRoom(people_ids=(npc.instance_id,))
        npc._room = room

        with _patch_instance(chars={npc.instance_id: npc}):
            hooks.fire_arrival(npc)

        assert seen == ["fired"]

    def test_pc_mover_no_entry_prog_on_self(self):
        seen = []
        pc = FakeChar(npc=False)
        pc.progs = {"entry_prog": [lambda: seen.append("fired")]}
        room = FakeRoom(people_ids=(pc.instance_id,))
        pc._room = room

        with _patch_instance(chars={pc.instance_id: pc}):
            hooks.fire_arrival(pc)

        assert seen == []

    def test_carried_item_entry_prog_fires(self):
        seen = []
        item = FakeItem()
        item.progs = {"entry_prog": [lambda: seen.append("item_entry")]}
        mover = FakeChar(npc=False, item_ids=(item.instance_id,))
        room = FakeRoom(people_ids=(mover.instance_id,))
        mover._room = room

        with _patch_instance(
            chars={mover.instance_id: mover},
            items={item.instance_id: item},
        ):
            hooks.fire_arrival(mover)

        assert seen == ["item_entry"]

    def test_greet_skips_mover(self):
        """The arriving char must not trigger its own greet_prog as a resident."""
        seen = []
        mover = FakeChar(npc=True)
        mover.progs = {"greet_prog": [lambda ch: seen.append(ch)]}
        room = FakeRoom(people_ids=(mover.instance_id,))
        mover._room = room

        with _patch_instance(chars={mover.instance_id: mover}):
            hooks.fire_arrival(mover)

        assert seen == []


# ---------------------------------------------------------------------------
# fire_speech tests
# ---------------------------------------------------------------------------

class TestFireSpeech:
    def test_mob_speech_prog_fires(self):
        seen = []
        mob = FakeChar(npc=True)
        mob.progs = {"speech_prog": [lambda ch, t: seen.append((ch, t))]}
        speaker = FakeChar(npc=False)
        room = FakeRoom(people_ids=(speaker.instance_id, mob.instance_id))
        speaker._room = room

        with _patch_instance(chars={speaker.instance_id: speaker, mob.instance_id: mob}):
            hooks.fire_speech(speaker, "hello")

        assert seen == [(speaker, "hello")]

    def test_speaker_mob_not_triggered(self):
        """A mob that is the speaker must not receive its own speech_prog."""
        seen = []
        mob_speaker = FakeChar(npc=True)
        mob_speaker.progs = {"speech_prog": [lambda ch, t: seen.append((ch, t))]}
        room = FakeRoom(people_ids=(mob_speaker.instance_id,))
        mob_speaker._room = room

        with _patch_instance(chars={mob_speaker.instance_id: mob_speaker}):
            hooks.fire_speech(mob_speaker, "hello")

        assert seen == []

    def test_room_item_speech_prog_fires(self):
        seen = []
        item = FakeItem()
        item.progs = {"speech_prog": [lambda ch, t: seen.append(t)]}
        speaker = FakeChar(npc=False)
        room = FakeRoom(
            people_ids=(speaker.instance_id,),
            item_ids=(item.instance_id,),
        )
        speaker._room = room

        with _patch_instance(
            chars={speaker.instance_id: speaker},
            items={item.instance_id: item},
        ):
            hooks.fire_speech(speaker, "world")

        assert seen == ["world"]

    def test_carried_item_speech_prog_fires(self):
        seen = []
        item = FakeItem()
        item.progs = {"speech_prog": [lambda ch, t: seen.append(t)]}
        carrier = FakeChar(npc=False, item_ids=(item.instance_id,))
        room = FakeRoom(people_ids=(carrier.instance_id,))
        carrier._room = room

        with _patch_instance(
            chars={carrier.instance_id: carrier},
            items={item.instance_id: item},
        ):
            hooks.fire_speech(carrier, "test")

        assert seen == ["test"]

    def test_room_speech_prog_fires(self):
        seen = []
        speaker = FakeChar(npc=False)
        room = FakeRoom(people_ids=(speaker.instance_id,))
        room.progs = {"speech_prog": [lambda ch, t: seen.append((ch, t))]}
        speaker._room = room

        with _patch_instance(chars={speaker.instance_id: speaker}):
            hooks.fire_speech(speaker, "hi room")

        assert seen == [(speaker, "hi room")]

    def test_no_room_is_safe(self):
        speaker = FakeChar(npc=False)
        speaker._room = None
        with _patch_instance():
            hooks.fire_speech(speaker, "test")  # must not raise

    def test_all_four_fire_in_order(self):
        """Verify ordering: mob → room_items → carried_items → room."""
        order = []
        mob = FakeChar(npc=True)
        mob.progs = {"speech_prog": [lambda ch, t: order.append("mob")]}
        room_item = FakeItem()
        room_item.progs = {"speech_prog": [lambda ch, t: order.append("room_item")]}
        carried = FakeItem()
        carried.progs = {"speech_prog": [lambda ch, t: order.append("carried")]}
        speaker = FakeChar(npc=False, item_ids=(carried.instance_id,))
        room = FakeRoom(
            people_ids=(speaker.instance_id, mob.instance_id),
            item_ids=(room_item.instance_id,),
        )
        room.progs = {"speech_prog": [lambda ch, t: order.append("room")]}
        speaker._room = room

        with _patch_instance(
            chars={speaker.instance_id: speaker, mob.instance_id: mob},
            items={room_item.instance_id: room_item, carried.instance_id: carried},
        ):
            hooks.fire_speech(speaker, "test")

        assert order == ["mob", "room_item", "carried", "room"]
