from tools.kbk_import import cparse, emit
from tools.kbk_import.resolve import Resolver

C = '''
const struct race_type race_table[] =
{
    {"null", FALSE, 0, 0, 0, 0, 0, 0, 0, 0},
    {"dwarf", TRUE, 0, AFF_INFRARED, 0, 0, RES_POISON | RES_DISEASE,
     VULN_DROWNING, A | H | M | V, A | B},
};
const struct pc_race_type pc_race_table[] =
{
    {"null race", "", 0, 0, {""}, {0, 0}, {13, 13, 13, 13, 13}, {18, 18, 18, 18, 18}, 0, FALSE},
    {"dwarf", "Dwarf", ALIGN_GN, 250, {"berserk"}, {1, 0},
     {2, -2, 1, -1, 3}, {22, 18, 22, 16, 25}, SIZE_MEDIUM, FALSE},
};
'''
DEFS = {"AFF_INFRARED": "128", "RES_POISON": "256", "RES_DISEASE": "512",
        "VULN_DROWNING": "1024", "A": "1", "B": "2", "H": "128", "M": "4096",
        "V": "2097152", "ALIGN_GN": "1", "SIZE_MEDIUM": "2"}
ORDER = ["warrior", "thief"]

MATERIALS = """* comment line
MATS
plastic~ 100 100 100 100 30
iron~ 110 120 110 100 130
"""

def test_emit_races():
    src = emit.emit_races(
        cparse.parse_braces(cparse.extract_initializer(C, "race_table")),
        cparse.parse_braces(cparse.extract_initializer(C, "pc_race_table")),
        Resolver(DEFS), ORDER)
    ns = {}
    exec(src, ns)
    assert ns["RACES"]["dwarf"]["res"] == 256 | 512
    assert "null" not in ns["PC_RACES"] and "null race" not in ns["PC_RACES"]
    d = ns["PC_RACES"]["dwarf"]
    assert d["skills"] == ["berserk"]
    assert d["classes"] == {"warrior": True, "thief": False}
    assert d["max_stats"] == [22, 18, 22, 16, 25]

def test_emit_materials():
    ns = {}
    exec(emit.emit_materials(MATERIALS), ns)
    assert ns["MATERIALS"]["iron"]["relative_weight"] == 130
    assert ns["MATERIALS"]["plastic"]["prot_magic"] == 100
