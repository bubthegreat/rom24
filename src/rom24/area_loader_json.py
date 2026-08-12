"""Load the world from per-area JSON folders (the successor to the `.are` loader).

Deserializes each ``areas/<name>/`` folder through the ``instance.from_json``
codec and reproduces the exact hand-off the legacy ``data_loader.load_area``
made to ``db.boot_db``: register templates, build the live Area instance,
instance each room, append resets to the area instance, and relink shop
back-references. Downstream boot steps (``area_update`` -> ``reset_area``,
``setup_exits``) then run unchanged.
"""
import importlib.util
import json
import logging
import os

from rom24 import instance, settings, merc, world_classes, object_creator, prog_triggers

logger = logging.getLogger(__name__)


def _load_progs(area_dir):
    """Import an area's progs.py (if present); its decorators self-register."""
    progs_path = os.path.join(area_dir, "progs.py")
    if not os.path.isfile(progs_path):
        return
    mod_name = "rom24_areaprogs_" + os.path.basename(area_dir.rstrip("/"))
    spec = importlib.util.spec_from_file_location(mod_name, progs_path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        logger.info("Loaded progs for area %s", os.path.basename(area_dir))
    except Exception:
        logger.exception("Failed to load progs for area %s", area_dir)


def _load(path):
    with open(path, "r") as fp:
        return json.load(fp, object_hook=instance.from_json)


def _area_dirs(areas_dir):
    dirs = []
    for name in sorted(os.listdir(areas_dir)):
        d = os.path.join(areas_dir, name)
        if name == "_global" or not os.path.isdir(d):
            continue
        if os.path.isfile(os.path.join(d, "area.json")):
            dirs.append(d)
    # Load in ascending area index, matching the legacy area.lst ordering.
    return sorted(dirs, key=lambda d: getattr(_load(os.path.join(d, "area.json")), "index", 0))


def _load_globals(areas_dir):
    gdir = os.path.join(areas_dir, "_global")

    helps = _load(os.path.join(gdir, "helps.json"))
    instance.helps.clear()
    instance.helps.update(helps)
    # do_help reads merc.help_list; the "$" terminator entry is excluded (as the
    # legacy loader did), and GREETING entries also feed greeting_list.
    merc.help_list.clear()
    merc.greeting_list.clear()
    for keyword, h in instance.helps.items():
        if keyword == "$":
            continue
        merc.help_list.append(h)
        if h.keyword == "GREETING":
            merc.greeting_list.append(h)

    socials = _load(os.path.join(gdir, "socials.json"))
    merc.social_list.clear()
    merc.social_list.extend(socials)
    instance.socials.clear()
    for social in socials:
        instance.socials[social.name] = social


def load_areas_json(areas_dir=None):
    areas_dir = areas_dir or settings.AREAS_DIR
    prog_triggers.clear()  # start clean so a re-load does not stack handlers

    for d in _area_dirs(areas_dir):
        area_tmpl = _load(os.path.join(d, "area.json"))
        instance.area_templates[area_tmpl.name] = area_tmpl
        area_inst = world_classes.Area(area_tmpl)  # live instance -> instance.areas

        for room in _load(os.path.join(d, "rooms.json")):
            instance.room_templates[room.vnum] = room
            room_inst = object_creator.create_room(room)
            room_inst.environment = area_inst.instance_id

        for mob in _load(os.path.join(d, "mobiles.json")):
            instance.npc_templates[mob.vnum] = mob
        for obj in _load(os.path.join(d, "objects.json")):
            instance.item_templates[obj.vnum] = obj

        area_inst.reset_list = _load(os.path.join(d, "resets.json"))

        for shop in _load(os.path.join(d, "shops.json")):
            instance.shop_templates[shop.keeper] = shop
            keeper = instance.npc_templates.get(shop.keeper)
            if keeper is not None:
                keeper.pShop = shop

        _load_progs(d)

    _load_globals(areas_dir)
