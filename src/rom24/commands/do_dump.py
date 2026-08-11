import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24.commands.do_memory import _memory_lines


def do_dump(ch, argument):
    """Faithful minimal port of stock ROM's do_dump.

    Stock do_dump writes a heavy debug report of data-structure usage to a file
    named ``mem.dmp`` in the current working directory. We keep the same fixed
    filename (safe: never an arbitrary/attacker-controlled path) and dump the
    same summary counts do_memory reports, then confirm to the immortal.
    """
    lines = _memory_lines()
    report = "\n".join(lines) + "\n"

    try:
        with open("mem.dmp", "w") as fp:
            fp.write(report)
    except OSError as exc:
        # If the cwd is not writable, fall back to logging only so the command
        # stays non-destructive and never raises at the immortal.
        logger.warning("do_dump: could not write mem.dmp: %s", exc)

    logger.info("do_dump memory report:\n%s", report)
    ch.send("Dumped.\n")


interp.register_command(
    interp.cmd_type("dump", do_dump, merc.POS_DEAD, merc.ML, merc.LOG_ALWAYS, 0)
)
