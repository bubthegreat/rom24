"""Behavioral tests for the five "info" commands that were marked broken.

Boots the world once (same pattern as tests/test_e2e_smoke.py) and exercises
each command against a minimal stub character whose ``send`` captures output.
"""
import pytest


class StubChar:
    """Minimal char: captures output and answers the few methods each command reads."""

    def __init__(self):
        self.messages = []
        self.in_room = None
        self.lines = 0
        self.desc = None

    def send(self, txt):
        self.messages.append(txt)

    @property
    def output(self):
        return "".join(self.messages)

    # do_rstat / do_count helpers
    def is_room_owner(self, location):
        return False

    def can_see(self, other):
        return True


# --- do_time -----------------------------------------------------------------
def test_do_time_shows_clock_and_startup(booted_world, command):

    ch = StubChar()
    command('time')(ch, "")
    out = ch.output
    assert "o'clock" in out
    assert "Month of" in out
    assert "ROM started up at" in out
    assert "The system time is" in out


def test_do_time_todo_removed(command_source):
    assert "Known broken" not in command_source('time')


# --- do_scroll ---------------------------------------------------------------
def test_do_scroll_sets_lines(booted_world, command):

    ch = StubChar()
    command('scroll')(ch, "50")
    # stock ROM stores lines - 2
    assert ch.lines == 48
    assert "Scroll set to 50 lines." in ch.output


def test_do_scroll_disable_and_reject(booted_world, command):

    ch = StubChar()
    ch.lines = 20
    command('scroll')(ch, "0")
    assert ch.lines == 0
    assert "Paging disabled." in ch.output

    ch2 = StubChar()
    command('scroll')(ch2, "5")  # below the reasonable range
    assert "reasonable number" in ch2.output

    ch3 = StubChar()
    command('scroll')(ch3, "notanumber")
    assert "must provide a number" in ch3.output


def test_do_scroll_todo_removed(command_source):
    assert "Known broken" not in command_source('scroll')


# --- do_count ----------------------------------------------------------------
def test_do_count_reports(booted_world, command):

    ch = StubChar()
    command('count')(ch, "")
    out = ch.output
    assert "characters on" in out
    assert "most so far today" in out


def test_do_count_todo_removed(command_source):
    assert "Known broken" not in command_source('count')


# --- do_rstat ----------------------------------------------------------------
def _room_with_exit():
    from rom24 import instance

    for room in instance.rooms.values():
        if any(e for e in room.exit):
            return room
    return None


def test_do_rstat_lists_exits(booted_world, command):

    room = _room_with_exit()
    assert room is not None, "no room with an exit was loaded"

    ch = StubChar()
    ch.in_room = room  # in_room == location skips the private-room check
    command('rstat')(ch, "")
    out = ch.output
    assert "Name:" in out
    assert "Vnum:" in out
    assert "Room flags:" in out
    assert "Door:" in out
    assert "Exit flags:" in out


def test_do_rstat_todo_removed(command_source):
    assert "Known broken" not in command_source('rstat')


# --- do_return ---------------------------------------------------------------
class _Desc:
    def __init__(self, original):
        self.original = original


def test_do_return_not_switched(booted_world, command):

    ch = StubChar()
    ch.desc = _Desc(original=None)
    command('return')(ch, "")
    assert "You aren't switched." in ch.output


def test_do_return_todo_removed(command_source):
    assert "Known broken" not in command_source('return')
