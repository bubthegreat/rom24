from tools.kbk_import import cparse, emit
from tools.kbk_import.resolve import Resolver

C = '''
const struct attack_type attack_table[MAX_DAMAGE_MESSAGE] =
{
    {"none", "hit", -1},
    {"slice", "slice", DAM_SLASH},
};
const struct str_app_type str_app[26] =
{
    {-5, -4, 0, 0},
    {-5, -4, 3, 1},
};
'''
DEFS = {"DAM_SLASH": "1"}


def test_emit_aux_attacks_and_apps():
    r = Resolver(DEFS)
    src = emit.emit_aux(
        {"attack_table": cparse.parse_braces(cparse.extract_initializer(C, "attack_table")),
         "str_app": cparse.parse_braces(cparse.extract_initializer(C, "str_app"))},
        r)
    ns = {}
    exec(src, ns)
    assert ns["ATTACKS"]["slice"] == {"name": "slice", "noun": "slice", "damage": 1}
    assert ns["STR_APP"][1] == [-5, -4, 3, 1]
