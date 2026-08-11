"""Content-pack discovery and load ordering.

A pack is a directory under ``settings.PACKS_DIR`` containing a ``pack.json``
manifest. Packs contribute static game tables (races, classes, skills, ...) and
declare the code directories that self-register commands/spells. This module
finds packs and orders them so every pack loads after the packs it depends on.
"""
import json
import logging
import os

from rom24 import settings

logger = logging.getLogger(__name__)


class Pack:
    def __init__(self, name, path, version="0.0.0", depends=None, data_dir=".", code_dirs=None):
        self.name = name
        self.path = path
        self.version = version
        self.depends = list(depends or [])
        self.data_dir = os.path.normpath(os.path.join(path, data_dir))
        self.code_dirs = list(code_dirs or [])

    def __repr__(self):
        return "Pack(%s @ %s)" % (self.name, self.path)


def _load_manifest(pack_dir):
    manifest_path = os.path.join(pack_dir, "pack.json")
    if not os.path.isfile(manifest_path):
        return None
    try:
        with open(manifest_path, "r") as fp:
            data = json.load(fp)
    except (ValueError, OSError) as exc:
        logger.error("Skipping pack '%s': bad manifest: %s", pack_dir, exc)
        return None
    name = data.get("name")
    if not name:
        logger.error("Skipping pack '%s': manifest has no 'name'.", pack_dir)
        return None
    return Pack(
        name=name,
        path=pack_dir,
        version=data.get("version", "0.0.0"),
        depends=data.get("depends", []),
        data_dir=data.get("data_dir", "."),
        code_dirs=data.get("code_dirs", []),
    )


def discover_packs(packs_root=None):
    if packs_root is None:
        packs_root = settings.PACKS_DIR
    found = []
    if not os.path.isdir(packs_root):
        logger.warning("Packs root does not exist: %s", packs_root)
        return found
    for name in sorted(os.listdir(packs_root)):
        pack_dir = os.path.join(packs_root, name)
        if not os.path.isdir(pack_dir):
            continue
        pack = _load_manifest(pack_dir)
        if pack is not None:
            found.append(pack)
    return found


def resolve_load_order(packs):
    by_name = {p.name: p for p in packs}
    ordered = []
    done = set()
    visiting = set()

    def visit(pack, chain):
        if pack.name in done:
            return
        if pack.name in visiting:
            raise ValueError("Pack dependency cycle: %s" % " -> ".join(chain + [pack.name]))
        visiting.add(pack.name)
        for dep in pack.depends:
            dep_pack = by_name.get(dep)
            if dep_pack is None:
                logger.warning("Pack '%s' depends on missing pack '%s'; ignoring.", pack.name, dep)
                continue
            visit(dep_pack, chain + [pack.name])
        visiting.discard(pack.name)
        done.add(pack.name)
        ordered.append(pack)

    for pack in sorted(packs, key=lambda p: p.name):
        visit(pack, [])
    return ordered
