"""Registry of the shared bit-flag tables, keyed by name and by identity.

``bit.Bit`` objects hold a reference to one of a handful of shared flag tables
(act_flags, imm_flags, ...). Serializing the whole table inside every Bit bloats
saves massively (a single mob template was ~36KB, mostly repeated flag tables).
Instead, a Bit that points at a registered table serializes only a short name
reference and rebuilds the table by name on load. Tables register themselves at
import (see ``tables.py``); anything unregistered falls back to embedding.
"""

_by_name = {}
_by_id = {}


def register(name, table):
    _by_name[name] = table
    _by_id[id(table)] = name


def name_for(table):
    """Return the registered name for a flag table object, or None."""
    return _by_id.get(id(table))


def table_for(name):
    """Return the flag table registered under ``name``, or None."""
    return _by_name.get(name)
