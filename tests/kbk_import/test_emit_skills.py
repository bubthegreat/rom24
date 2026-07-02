from tools.kbk_import import cparse, emit
from tools.kbk_import.resolve import Resolver

C = '''
const struct skill_type skill_table[MAX_SKILL] =
{
    {"reserved", {99, 99}, {99, 99}, 0, TAR_IGNORE, POS_STANDING,
     NULL, SLOT(0), 0, 0, "", "", "", CMD_NONE},
    {"acid blast", {53, 33}, {1, 1}, spell_acid_blast, TAR_CHAR_OFFENSIVE,
     POS_FIGHTING, &gsn_acid, SLOT(70), 20, 24, "acid blast", "!Acid Blast!", "", CMD_SPELL},
};
const struct group_type group_table[MAX_GROUP] =
{
    {"class basics", {1, 3}, {"acid blast"}},
};
'''
DEFS = {"TAR_IGNORE": "0", "TAR_CHAR_OFFENSIVE": "1", "POS_STANDING": "8",
        "POS_FIGHTING": "7", "CMD_NONE": "0", "CMD_SPELL": "1", "spell_beast_call": "spell_beast_call"}
ORDER = ["warrior", "thief"]

def test_emit_skills():
    entries = cparse.parse_braces(cparse.extract_initializer(C, "skill_table"))
    src = emit.emit_skills(entries, Resolver(DEFS), ORDER)
    ns = {}
    exec(src, ns)
    assert "reserved" not in ns["SKILLS"]
    s = ns["SKILLS"]["acid blast"]
    assert s["skill_level"] == {"warrior": 53, "thief": 33}
    assert s["spell_fun"] == "acid blast"
    assert s["pgsn"] == "acid"
    assert s["slot"] == 70 and s["beats"] == 24 and s["ctype"] == 1

def test_emit_groups():
    entries = cparse.parse_braces(cparse.extract_initializer(C, "group_table"))
    src = emit.emit_groups(entries, Resolver(DEFS), ORDER)
    ns = {}
    exec(src, ns)
    g = ns["GROUPS"]["class basics"]
    assert g["rating"] == {"warrior": 1, "thief": 3}
    assert g["spells"] == ["acid blast"]


def test_emit_skills_tolerates_truncated_entries():
    c = '''
const struct skill_type skill_table[MAX_SKILL] =
{
    {"awareness", {53, 33}, {1, 1}, spell_null, TAR_IGNORE, POS_STANDING,
     &gsn_awareness, SLOT(0), 0, 0, "", ""},
};
'''
    entries = cparse.parse_braces(cparse.extract_initializer(c, "skill_table"))
    ns = {}
    exec(emit.emit_skills(entries, Resolver(DEFS), ORDER), ns)
    s = ns["SKILLS"]["awareness"]
    assert s["msg_obj"] == "" and s["ctype"] == 0


def test_emit_skills_duplicate_names_first_wins():
    c = '''
const struct skill_type skill_table[MAX_SKILL] =
{
    {"beast call", {53, 33}, {1, 1}, spell_beast_call, TAR_IGNORE, POS_STANDING,
     NULL, SLOT(0), 50, 12, "", "", "", CMD_SPELL},
    {"beast call", {53, 33}, {1, 1}, spell_null, TAR_IGNORE, POS_STANDING,
     NULL, SLOT(0), 0, 0, "", "", "", CMD_NONE},
};
'''
    entries = cparse.parse_braces(cparse.extract_initializer(c, "skill_table"))
    ns = {}
    exec(emit.emit_skills(entries, Resolver(DEFS), ORDER), ns)
    assert ns["SKILLS"]["beast call"]["min_mana"] == 50   # first entry kept
    assert ns["SKILLS"]["beast call"]["spell_fun"] == "beast call"
