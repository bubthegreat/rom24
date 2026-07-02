from tools.kbk_import import cparse, emit
from tools.kbk_import.resolve import Resolver

C = '''
const struct class_type class_table[MAX_CLASS] =
{
    {"warrior", "War", ALIGN_ANY, 0, OBJ_VNUM_SCHOOL_SWORD,
     {3022, 8818, 20408}, 75, 20, -10, 8, 19, FALSE,
     "class basics", "class default", CLASS_FIGHTER},
};
'''
DEFS = {"ALIGN_ANY": "3", "OBJ_VNUM_SCHOOL_SWORD": "3700", "CLASS_FIGHTER": "0"}

def test_emit_classes_roundtrips_through_exec():
    entries = cparse.parse_braces(cparse.extract_initializer(C, "class_table"))
    src, order = emit.emit_classes(entries, Resolver(DEFS))
    assert order == ["warrior"]
    ns = {}
    exec(src, ns)  # generated module must be valid python
    w = ns["CLASSES"]["warrior"]
    assert w["who_name"] == "War"
    assert w["guild_rooms"] == [3022, 8818, 20408]
    assert w["weapon"] == 3700
    assert w["f_mana"] is False
    assert w["thac0_32"] == -10
    assert ns["CLASS_ORDER"] == ["warrior"]

def test_emit_constants():
    src = emit.emit_constants({"MAX_LEVEL": "60", "LEVEL_HERO": "(MAX_LEVEL - 9)",
                               "WEIGHT_STANDARD": "30",
                               "AC_PER_ONE_PERCENT_DECREASE_DAMAGE": "-75.0"})
    ns = {}
    exec(src, ns)
    assert ns["MAX_LEVEL"] == 60 and ns["LEVEL_HERO"] == 51
    assert ns["WEIGHT_STANDARD"] == 30
    assert ns["AC_PER_ONE_PERCENT_DECREASE_DAMAGE"] == -75.0
