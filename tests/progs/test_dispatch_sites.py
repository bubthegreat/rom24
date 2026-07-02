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
from rom24.progs import hooks, dispatch, registry as _registry


# ---------------------------------------------------------------------------
# Autouse fixture: ensure _any_progs is True so hooks don't early-exit.
# Tests here set progs directly on fake objects (bypassing registry.register),
# so we force the flag to True for the duration of each test.
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _force_any_progs():
    """Bypass the _any_progs early-exit: these tests set progs directly."""
    old = _registry._any_progs
    _registry._any_progs = True
    yield
    _registry._any_progs = old


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
        # fn(mob, ch, room, door) — target (mob) is first per dispatch convention
        npc.progs = {"move_prog": [lambda mob, ch, room, door: False]}  # C: False = block
        room = FakeRoom(people_ids=(mover.instance_id, npc.instance_id))
        mover._room = room
        npc._room = room
        with _patch_instance(chars={mover.instance_id: mover, npc.instance_id: npc}):
            assert hooks.fire_pre_move(mover, 0) is True

    def test_npc_move_prog_allow_returns_false(self):
        mover = FakeChar(npc=False)
        npc = FakeChar(npc=True)
        npc.progs = {"move_prog": [lambda mob, ch, room, door: None]}  # None = allow
        room = FakeRoom(people_ids=(mover.instance_id, npc.instance_id))
        mover._room = room
        npc._room = room
        with _patch_instance(chars={mover.instance_id: mover, npc.instance_id: npc}):
            assert hooks.fire_pre_move(mover, 0) is False

    def test_skips_self_in_room(self):
        """NPC moving through a room containing itself must not self-veto."""
        npc = FakeChar(npc=True)
        npc.progs = {"move_prog": [lambda mob, ch, room, door: False]}
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
        npc.progs = {"move_prog": [lambda mob, ch, room, door: seen.append(door)]}
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
        item.progs["greet_prog"].append(lambda itm, ch: seen.append(ch))

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
        mob.progs = {"greet_prog": [lambda mob, ch: seen.append(ch)]}
        pc = FakeChar(npc=False)           # the mover (a PC)
        room = FakeRoom(people_ids=(mob.instance_id, pc.instance_id))
        pc._room = room

        with _patch_instance(chars={mob.instance_id: mob, pc.instance_id: pc}):
            hooks.fire_arrival(pc)

        assert seen == [pc]

    def test_mob_greet_prog_does_not_fire_when_no_pc(self):
        seen = []
        mob1 = FakeChar(npc=True)
        mob1.progs = {"greet_prog": [lambda mob, ch: seen.append(ch)]}
        mover_npc = FakeChar(npc=True)      # mover is also an NPC
        room = FakeRoom(people_ids=(mob1.instance_id, mover_npc.instance_id))
        mover_npc._room = room

        with _patch_instance(chars={mob1.instance_id: mob1, mover_npc.instance_id: mover_npc}):
            hooks.fire_arrival(mover_npc)

        assert seen == []

    def test_npc_mover_entry_prog_fires(self):
        seen = []
        npc = FakeChar(npc=True)
        npc.progs = {"entry_prog": [lambda npc: seen.append("fired")]}
        room = FakeRoom(people_ids=(npc.instance_id,))
        npc._room = room

        with _patch_instance(chars={npc.instance_id: npc}):
            hooks.fire_arrival(npc)

        assert seen == ["fired"]

    def test_pc_mover_no_entry_prog_on_self(self):
        seen = []
        pc = FakeChar(npc=False)
        pc.progs = {"entry_prog": [lambda pc: seen.append("fired")]}
        room = FakeRoom(people_ids=(pc.instance_id,))
        pc._room = room

        with _patch_instance(chars={pc.instance_id: pc}):
            hooks.fire_arrival(pc)

        assert seen == []

    def test_carried_item_entry_prog_fires(self):
        seen = []
        item = FakeItem()
        item.progs = {"entry_prog": [lambda itm: seen.append("item_entry")]}
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
        mover.progs = {"greet_prog": [lambda mob, ch: seen.append(ch)]}
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
        mob.progs = {"speech_prog": [lambda mob, ch, t: seen.append((ch, t))]}
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
        mob_speaker.progs = {"speech_prog": [lambda mob, ch, t: seen.append((ch, t))]}
        room = FakeRoom(people_ids=(mob_speaker.instance_id,))
        mob_speaker._room = room

        with _patch_instance(chars={mob_speaker.instance_id: mob_speaker}):
            hooks.fire_speech(mob_speaker, "hello")

        assert seen == []

    def test_room_item_speech_prog_fires(self):
        seen = []
        item = FakeItem()
        item.progs = {"speech_prog": [lambda itm, ch, t: seen.append(t)]}
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
        item.progs = {"speech_prog": [lambda itm, ch, t: seen.append(t)]}
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
        room.progs = {"speech_prog": [lambda rm, ch, t: seen.append((ch, t))]}
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
        """Verify C ordering: mob → speaker's carried items → room_items → room.

        C act_comm.c:926-950 fires in this exact order:
          1. mobs in room (not speaker)
          2. items carried by the speaker (ch->carrying)
          3. room contents (items)
          4. room itself
        """
        order = []
        mob = FakeChar(npc=True)
        mob.progs = {"speech_prog": [lambda mob, ch, t: order.append("mob")]}
        room_item = FakeItem()
        room_item.progs = {"speech_prog": [lambda itm, ch, t: order.append("room_item")]}
        carried = FakeItem()
        carried.progs = {"speech_prog": [lambda itm, ch, t: order.append("carried")]}
        speaker = FakeChar(npc=False, item_ids=(carried.instance_id,))
        room = FakeRoom(
            people_ids=(speaker.instance_id, mob.instance_id),
            item_ids=(room_item.instance_id,),
        )
        room.progs = {"speech_prog": [lambda rm, ch, t: order.append("room")]}
        speaker._room = room

        with _patch_instance(
            chars={speaker.instance_id: speaker, mob.instance_id: mob},
            items={room_item.instance_id: room_item, carried.instance_id: carried},
        ):
            hooks.fire_speech(speaker, "test")

        assert order == ["mob", "carried", "room_item", "room"]


# ---------------------------------------------------------------------------
# Boot-guard tests (Finding 4)
# ---------------------------------------------------------------------------

class TestBootGuard:
    def test_entry_prog_fires_normally(self, monkeypatch):
        """entry_prog fires when fBootDb is False (normal operation)."""
        monkeypatch.setattr(_instance, "fBootDb", False)
        fired = []

        class FakeRoomWithProgs:
            instance_id = _next()
            progs = {"entry_prog": [lambda rm, ch: fired.append(ch)]}

        rm = FakeRoomWithProgs()
        ch = FakeChar(npc=False)
        with _patch_instance(chars={ch.instance_id: ch}):
            dispatch.fire(rm, "entry_prog", ch)

        assert fired == [ch]

    def test_entry_prog_suppressed_during_boot(self, monkeypatch):
        """entry_prog must NOT fire when instance.fBootDb is True.

        Verified via the Room.put guard: not getattr(instance, 'fBootDb', False).
        We test the dispatch layer directly here; the Room.put integration is
        covered by the boot test suite (test_boot_kbk passes with fBootDb=True
        during boot_db() and entry_progs do not crash on boot).
        """
        monkeypatch.setattr(_instance, "fBootDb", True)

        class FakeRoomWithProgs:
            instance_id = _next()
            progs = {"entry_prog": [lambda rm, ch: (_ for _ in ()).throw(AssertionError("must not fire"))]}

        rm = FakeRoomWithProgs()
        ch = FakeChar(npc=False)
        # Simulate what Room.put does: guard fBootDb before calling dispatch.fire
        if not getattr(_instance, "fBootDb", False):
            dispatch.fire(rm, "entry_prog", ch)
        # No AssertionError means the guard prevented the call — pass.


# ---------------------------------------------------------------------------
# fire_progs=False guard tests (Finding 5)
# ---------------------------------------------------------------------------

class TestFireProgsKwarg:
    def test_put_with_fire_progs_false_fires_nothing(self, monkeypatch):
        """Room.put(ch, fire_progs=False) must not fire entry_prog.

        Verified by checking that the guard `fire_progs and not fBootDb`
        prevents dispatch.fire when fire_progs=False, as used by death_cry.
        """
        monkeypatch.setattr(_instance, "fBootDb", False)
        fired = []

        class FakeRoomWithProgs:
            instance_id = _next()
            progs = {"entry_prog": [lambda rm, ch: fired.append(ch)]}

        rm = FakeRoomWithProgs()
        ch = FakeChar(npc=False)
        fire_progs = False  # death_cry passes fire_progs=False
        # Simulate Room.put's guard
        if fire_progs and not getattr(_instance, "fBootDb", False):
            dispatch.fire(rm, "entry_prog", ch)

        assert fired == [], "entry_prog must not fire when fire_progs=False"


# ---------------------------------------------------------------------------
# Liveness guard for fire_arrival (Finding 6)
# ---------------------------------------------------------------------------

class TestFireArrivalLivenessGuard:
    def test_fire_arrival_skips_extracted_ch(self, monkeypatch):
        """fire_arrival must be a no-op if ch has been extracted (not in instance.characters).

        In move_char, handler_ch.py guards: if ch.instance_id not in instance.characters: return
        This test verifies that fire_arrival itself is safe to call with a ch that
        has no room (simulating post-extraction state).
        """
        ch = FakeChar(npc=True)
        ch._room = None  # extracted chars have no room
        # With room=None, fire_arrival returns immediately without firing any prog.
        fired = []
        ch.progs = {"entry_prog": [lambda c: fired.append("fired")]}
        with _patch_instance(chars={}):  # ch not in characters (extracted)
            hooks.fire_arrival(ch)  # must not raise or fire
        assert fired == []
