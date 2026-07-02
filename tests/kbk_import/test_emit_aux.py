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


C2 = '''
const struct liq_type liq_table[LIQ_MAX] =
{
    {"water", "clear", {0, 1, 10, 0, 16}},
};
const struct dex_app_type dex_app[26] =
{
    {60, 0},
    {50, 0},
};
'''


def test_emit_aux_liq_flatten_and_dex_truncation():
    r = Resolver({})
    src = emit.emit_aux(
        {"liq_table": cparse.parse_braces(cparse.extract_initializer(C2, "liq_table")),
         "dex_app": cparse.parse_braces(cparse.extract_initializer(C2, "dex_app"))},
        r)
    ns = {}
    exec(src, ns)
    assert ns["LIQUIDS"]["water"] == {"name": "water", "color": "clear", "proof": 0,
                                      "full": 1, "thirst": 10, "food": 0, "ssize": 16}
    assert ns["DEX_APP"][1] == [50]
