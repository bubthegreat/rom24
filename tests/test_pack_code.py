"""A content pack can ship its own command code, loaded from its folder."""
import json
import os

CMD_SRC = '''
from rom24 import interp, merc


def do_zzztest(ch, argument):
    ch.send("zzztest ran\\n")


interp.register_command(
    interp.cmd_type("zzztest", do_zzztest, merc.POS_DEAD, 0, merc.LOG_NORMAL, 1)
)
'''


def test_pack_ships_a_command(booted_world, tmp_path):
    from rom24 import packs, interp

    root = str(tmp_path)
    pack = os.path.join(root, "zzcmdpack")
    os.makedirs(os.path.join(pack, "commands"))
    with open(os.path.join(pack, "pack.json"), "w") as fp:
        json.dump({"name": "zzcmdpack", "version": "1.0.0", "code_dirs": ["commands"]}, fp)
    with open(os.path.join(pack, "commands", "do_zzztest.py"), "w") as fp:
        fp.write(CMD_SRC)

    assert "zzztest" not in interp.cmd_table
    packs.load_pack_code(root)
    assert "zzztest" in interp.cmd_table, "pack command did not self-register"


def test_core_dotted_code_dirs_are_skipped(booted_world, tmp_path):
    # A pack whose code_dirs point at an installed package (rom24.*) is a no-op
    # here (hotfix loads those); it must not raise.
    from rom24 import packs

    root = str(tmp_path)
    pack = os.path.join(root, "coreish")
    os.makedirs(pack)
    with open(os.path.join(pack, "pack.json"), "w") as fp:
        json.dump(
            {"name": "coreish", "version": "1.0.0", "code_dirs": ["rom24.commands"]}, fp
        )
    packs.load_pack_code(root)  # must not raise
