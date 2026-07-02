from tools.kbk_import import cparse

C_SNIPPET = r'''
/* a comment { with braces } */
#define ALIGN_ANY 3 // trailing comment
#define MSL (2*4096)
const struct class_type class_table[MAX_CLASS] =
    {
        {// 0
         "warrior",
         "War",
         ALIGN_ANY,
         0,
         OBJ_VNUM_SCHOOL_SWORD,
         {3022, 8818, 20408},
         75, 20, -10, 8, 19,
         FALSE,
         "class basics",
         "class default",
         CLASS_FIGHTER},
        {"thief", "Thi", ALIGN_ANY, 0, OBJ_VNUM_SCHOOL_DAGGER,
         {3028, 8850, 20525}, 75, 20, -4, 8, 17, FALSE,
         "class basics", "class default", CLASS_FIGHTER},
};
'''

def test_strip_comments_removes_both_styles():
    out = cparse.strip_comments(C_SNIPPET)
    assert "a comment" not in out and "trailing comment" not in out
    assert '"warrior"' in out

def test_strip_comments_keeps_comment_chars_inside_strings():
    assert cparse.strip_comments('x = "a /* not */ comment";') == 'x = "a /* not */ comment";'

def test_parse_defines():
    d = cparse.parse_defines(C_SNIPPET)
    assert d["ALIGN_ANY"] == "3"
    assert d["MSL"] == "(2*4096)"

def test_extract_initializer_and_parse():
    block = cparse.extract_initializer(C_SNIPPET, "class_table")
    entries = cparse.parse_braces(block)
    assert len(entries) == 2
    warrior = entries[0]
    assert warrior[0] == ("str", "warrior")
    assert warrior[1] == ("str", "War")
    assert warrior[2] == "ALIGN_ANY"
    assert warrior[5] == ["3022", "8818", "20408"]
    assert warrior[11] == "FALSE"
    assert warrior[14] == "CLASS_FIGHTER"


def test_adjacent_string_literals_concatenate():
    assert cparse.parse_braces('{"hello" " world"}') == [("str", "hello world")]
    assert cparse.parse_braces('{"a", "b"}') == [("str", "a"), ("str", "b")]
