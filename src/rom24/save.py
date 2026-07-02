import os
import json
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)

from rom24 import object_creator
from rom24 import instance
from rom24.merc import *
from rom24 import tables
from rom24 import world_classes
from rom24 import settings
from rom24 import handler_pc
from rom24 import auth


def legacy_load_char_obj(d, name):
    """No legacy players in KBK world; always report not-found."""
    ch = handler_pc.Pc(name)
    return False, ch


def fwrite_obj(ch, obj, contained_by=None):
    odict = OrderedDict()
    obj = instance.items[obj]
    odict["Vnum"] = obj.vnum
    odict["Enchanted"] = obj.enchanted
    odict["Name"] = obj.name
    odict["ShD"] = obj.short_descr
    odict["Desc"] = obj.description
    odict["ExtF"] = obj.extra_flags
    odict["WeaF"] = obj.wear_flags
    odict["Ityp"] = obj.item_type
    odict["Wt"] = obj.weight
    odict["Cond"] = obj.condition

    odict["Wear"] = obj.wear_loc
    odict["Lev"] = obj.level
    odict["timer"] = obj.timer
    odict["cost"] = obj.cost
    odict["Val"] = obj.value

    odict["affected"] = [a for a in obj.affected if a.type >= 0]
    odict["ExDe"] = {ed.keyword: ed.description for ed in obj.extra_descr}
    if contained_by:
        odict["In"] = contained_by.instance_id
    if obj.contents:
        odict["inventory"] = [fwrite_obj(ch, o, obj) for o in obj.inventory]
    return odict


