from collections import OrderedDict, namedtuple
import logging

logger = logging.getLogger(__name__)

clan_type = namedtuple("clan_type", "name, who_name, hall, independent")
clan_table: dict = OrderedDict()

position_type = namedtuple("position_type", "name, short_name")
position_table: dict = OrderedDict()

sex_table: dict = OrderedDict()

# for sizes */
size_table: list = []

# various flag tables */
flag_type = namedtuple("flag_type", "name, bit, settable")
act_flags: dict = OrderedDict()
plr_flags: dict = OrderedDict()
affect_flags: dict = OrderedDict()
off_flags: dict = OrderedDict()
imm_flags: dict = OrderedDict()
form_flags: dict = OrderedDict()
part_flags: dict = OrderedDict()
comm_flags: dict = OrderedDict()
exit_flags: dict = OrderedDict()
vuln_flags: dict = OrderedDict()

# Register the shared flag tables so bit.Bit can serialize a short name
# reference instead of embedding the whole table. read_tables fills these
# OrderedDicts in place, preserving identity, so the references stay valid.
from rom24 import flag_registry as _flag_registry

for _flag_name, _flag_table in (
    ("act_flags", act_flags),
    ("plr_flags", plr_flags),
    ("affect_flags", affect_flags),
    ("off_flags", off_flags),
    ("imm_flags", imm_flags),
    ("form_flags", form_flags),
    ("part_flags", part_flags),
    ("comm_flags", comm_flags),
    ("exit_flags", exit_flags),
    ("vuln_flags", vuln_flags),
):
    _flag_registry.register(_flag_name, _flag_table)
