from tools.kbk_import import cparse, emit

C = '''
char *const title_table[MAX_CLASS][MAX_LEVEL + 1][2] =
{
    {
        {"Man", "Woman"},
        {"Swordpupil", "Swordpupil"},
        {"Recruit", "Recruit"},
    },
    {
        {"Man", "Woman"},
        {"Pickpocket", "Pickpocket"},
        {"Footpad", "Footpad"},
    },
};
'''


def test_extract_initializer_multidim():
    block = cparse.extract_initializer(C, "title_table")
    entries = cparse.parse_braces(block)
    assert len(entries) == 2
    assert entries[0][1] == [("str", "Swordpupil"), ("str", "Swordpupil")]


def test_emit_titles():
    entries = cparse.parse_braces(cparse.extract_initializer(C, "title_table"))
    src = emit.emit_titles(entries, ["warrior", "thief"])
    ns = {}
    exec(src, ns)
    assert ns["TITLES"]["warrior"][1] == ["Swordpupil", "Swordpupil"]
    assert ns["TITLES"]["thief"][2] == ["Footpad", "Footpad"]
