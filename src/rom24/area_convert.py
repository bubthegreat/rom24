"""One-shot converter: legacy `.are` world -> per-area JSON folders.

Assumes the world is already booted (templates populated in ``instance.*``).
Serializes each area's templates through the generic ``instance.to_json`` codec
into ``areas/<name>/`` folders, plus global helps/socials into ``_global/``.

This is the migration tool used to produce ``src/areas``. It reuses the legacy
loader only indirectly (via an already-booted world), so it must run before the
legacy `.are` loader is removed.
"""
import json
import logging
import os

from rom24 import instance, settings, merc

logger = logging.getLogger(__name__)


def _dump(obj):
    """Round-trip an object to plain JSON-able data via the shared codec."""
    return json.loads(json.dumps(obj, default=instance.to_json))


def _write(folder, fname, blob):
    with open(os.path.join(folder, fname), "w") as fp:
        json.dump(blob, fp, indent=2, sort_keys=True)


def _safe_name(name):
    return "".join(c if c.isalnum() else "_" for c in name).strip("_").lower()


def _area_instance_for(name):
    for inst in instance.areas.values():
        if getattr(inst, "name", None) == name:
            return inst
    return None


def convert_all(out_dir=None):
    out_dir = out_dir or settings.AREAS_DIR
    os.makedirs(out_dir, exist_ok=True)
    summary = {"areas": 0, "rooms": 0, "mobiles": 0, "objects": 0, "shops": 0, "resets": 0}

    for name, area_tmpl in instance.area_templates.items():
        folder = os.path.join(out_dir, _safe_name(name))
        os.makedirs(folder, exist_ok=True)

        rooms = [r for r in instance.room_templates.values() if r.area == name]
        mobs = [m for m in instance.npc_templates.values() if m.area == name]
        objs = [o for o in instance.item_templates.values() if o.area == name]
        shops = [
            s
            for s in instance.shop_templates.values()
            if instance.npc_templates.get(s.keeper) is not None
            and instance.npc_templates[s.keeper].area == name
        ]

        area_inst = _area_instance_for(name)
        resets = list(getattr(area_inst, "reset_list", []) or [])

        # Strip the pShop back-ref before dumping mobiles; it is rebuilt from
        # shops.json on load, and dumping it would embed the whole Shop.
        mob_blobs = []
        for m in mobs:
            saved = getattr(m, "pShop", None)
            m.pShop = None
            try:
                mob_blobs.append(_dump(m))
            finally:
                m.pShop = saved

        _write(folder, "area.json", _dump(area_tmpl))
        _write(folder, "rooms.json", [_dump(r) for r in rooms])
        _write(folder, "mobiles.json", mob_blobs)
        _write(folder, "objects.json", [_dump(o) for o in objs])
        _write(folder, "resets.json", [_dump(r) for r in resets])
        _write(folder, "shops.json", [_dump(s) for s in shops])

        summary["areas"] += 1
        summary["rooms"] += len(rooms)
        summary["mobiles"] += len(mobs)
        summary["objects"] += len(objs)
        summary["shops"] += len(shops)
        summary["resets"] += len(resets)

    gdir = os.path.join(out_dir, "_global")
    os.makedirs(gdir, exist_ok=True)
    _write(gdir, "helps.json", _dump(instance.helps))
    _write(gdir, "socials.json", _dump(merc.social_list))
    logger.info("Converted areas: %s", summary)
    return summary
