from rom24 import static_tables


def test_static_tables_shapes():
    assert set(static_tables.FLAG_TABLES) >= {
        "act_flags", "plr_flags", "affect_flags", "off_flags", "imm_flags",
        "form_flags", "part_flags", "comm_flags", "exit_flags"}
    assert static_tables.SIZE_TABLE and static_tables.POSITION_TABLE
