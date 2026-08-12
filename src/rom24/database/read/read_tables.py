import json
import logging
import os

from rom24 import settings
from rom24.database.tracker import tables

logger = logging.getLogger(__name__)


def _default_locs():
    from rom24 import packs

    ordered = packs.resolve_load_order(packs.discover_packs())
    return [p.data_dir for p in ordered]


def read_tables(listener=None, locs=None, extn=settings.DATA_EXTN):
    if locs is None:
        locs = _default_locs()

    if listener:
        # This means the game is running. Wipe the current data.
        logger.debug("Clearing all tables.")
        for tok in tables:
            if not tok.filter:
                tok.table.clear()
            else:
                affected = tok.filter(tok.table)
                for k in list(tok.table.keys()):
                    if k in affected:
                        del tok.table[k]
        listener.send("Tables cleared. Rebuilding...\n")

    logger.info("    Loading Tables from %d location(s).", len(locs))
    for tok in tables:
        seen_source = {}  # key -> loc that first supplied it
        for loc in locs:
            path = "%s%s" % (os.path.join(loc, tok.name), extn)
            if not os.path.isfile(path):
                continue
            try:
                with open(path, "r") as fp:
                    data = json.load(fp)
            except (ValueError, OSError) as exc:
                logger.error("Skipping bad table file %s: %s", path, exc)
                continue
            if isinstance(data, list):
                for v in data:
                    tok.table.append(v)
                continue
            for k, v in data.items():
                if isinstance(k, str) and k.isdigit():
                    k = int(k)
                override = isinstance(v, dict) and v.pop("__override__", False)
                if k in seen_source and not override:
                    raise ValueError(
                        "Table '%s' key %r defined by both %s and %s"
                        % (tok.name, k, seen_source[k], loc)
                    )
                if k in seen_source and override:
                    logger.info("Table '%s' key %r overridden by %s", tok.name, k, loc)
                tok.table[k] = tok.tupletype._make(v) if tok.tupletype else v
                seen_source[k] = loc
