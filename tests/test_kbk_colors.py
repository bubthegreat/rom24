"""Tests for KBK rom-scheme color code rendering through the pyom pipeline.

Task 9: ensures {R-style (rom-scheme) tokens in KBK area files are converted
to [R-style (pyom-scheme) tokens at load time so the existing send pipeline
(color_convert(text, "pyom", terminal)) can render them as ANSI color.
"""
import pathlib
import re

import pytest

from rom24 import data_loader
from rom24.miniboa import terminal as miniboa_terminal

_KBK_AREAS = pathlib.Path(__file__).parent.parent / "src" / "area" / "kbk"


# ---------------------------------------------------------------------------
# Unit tests — no area files required
# ---------------------------------------------------------------------------


def test_kbk_text_converts_rom_tokens_to_pyom():
    """ANSI round-trip: {RHello{x world yields correct ANSI after the pipeline.

    _kbk_text must produce pyom tokens ([R, [x) so that the send pipeline's
    color_convert("pyom", terminal) can render ANSI bold-red and reset.
    """
    out = data_loader._kbk_text("{RHello{x world")
    # stored text should carry pyom tokens
    assert "[R" in out, "rom {R should become pyom [R"
    assert "[x" in out, "rom {x should become pyom [x"
    assert "{R" not in out, "rom token {R must not survive conversion"
    # full send-time round-trip to ANSI
    ansi = miniboa_terminal.color_convert(out, "pyom", "ansi")
    assert "\033[1;31m" in ansi, "Expected ANSI bold-red from {R"
    assert "\033[0m" in ansi, "Expected ANSI reset from {x"
    assert "{R" not in ansi, "No rom token should survive in ANSI output"


def test_kbk_text_preserves_literal_brackets_alongside_colors():
    """Ordering test: escape-first then convert is the only correct order.

    A text containing BOTH a literal '[' AND a rom color code must have both
    rendered correctly.

    If we converted first ({G -> [G) and then escaped, the freshly created [G
    would be re-escaped to [[G, destroying the color token.  Escaping first
    ([bracket] -> [[bracket]]) and then converting ({G -> [G) is the only safe
    order: the literal brackets are protected before new tokens are introduced.
    """
    out = data_loader._kbk_text("[bracket] and {G green{x text")
    # literal '[' and ']' must be pyom-escaped
    assert "[[bracket]]" in out, "Literal [bracket] should be pyom-escaped to [[bracket]]"
    # {G must become the pyom bold-green token
    assert "[G" in out, "rom {G should become pyom [G"
    # full round-trip to ANSI
    ansi = miniboa_terminal.color_convert(out, "pyom", "ansi")
    assert "[bracket]" in ansi, "Literal [bracket] must survive to ANSI output as [bracket]"
    assert "\033[1;32m" in ansi, "Expected ANSI bold-green from {G"
    assert "{G" not in ansi, "No rom token should survive in ANSI output"


def test_kbk_text_reset_and_control_tokens():
    """{x reset and {* bell and {/ newline must round-trip through the pipeline."""
    out = data_loader._kbk_text("{x text")
    assert "[x" in out and "{x" not in out
    ansi = miniboa_terminal.color_convert(out, "pyom", "ansi")
    assert "\033[0m" in ansi

    out2 = data_loader._kbk_text("{* beep")
    assert "[*" in out2 and "{*" not in out2

    out3 = data_loader._kbk_text("{/ newline")
    assert "[/" in out3 and "{/" not in out3


def test_kbk_text_passthrough_on_plain_text():
    """Text with no color codes must survive _kbk_text unchanged (modulo [[/]])."""
    plain = "Hello, world! No colors here."
    out = data_loader._kbk_text(plain)
    assert out == plain, "Plain text must pass through _kbk_text unchanged"


def test_kbk_text_literal_brace_in_rom_format():
    """{{ (rom escape for literal {) becomes a plain { in pyom output."""
    out = data_loader._kbk_text("{{brace}}")
    # {{ -> '{' and }} -> '}' via rom->pyom conversion
    assert out == "{brace}", f"{{{{brace}}}} should become {{brace}}, got {out!r}"
    # round-trip: { and } are not special in pyom, so they pass through
    ansi = miniboa_terminal.color_convert(out, "pyom", "ansi")
    assert "{brace}" in ansi


# ---------------------------------------------------------------------------
# Real-data smoke test — requires KBK area files (make import-kbk)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not (_KBK_AREAS / "midgaard.are").exists(),
    reason="run make import-kbk first — KBK area files not found",
)
def test_kbk_text_real_data_room_3055_midgaard():
    """Real-data smoke: room 3055 in midgaard.are has {G/{x codes in its DESCR.

    After _kbk_text processing (as load_rooms_new applies), no rom-scheme
    tokens should survive, and the ANSI round-trip must yield green color.
    """
    area_file = _KBK_AREAS / "midgaard.are"
    content = area_file.read_text(encoding="latin-1")
    m = re.search(r"#3055.*?DESCR\s*\n(.*?)~", content, re.DOTALL)
    assert m is not None, "Could not find DESCR for room 3055 in midgaard.are"
    raw_descr = m.group(1)
    assert "{G" in raw_descr, "Precondition: room 3055 DESCR must contain {G"

    out = data_loader._kbk_text(raw_descr)
    assert "{G" not in out, "rom {G must be converted to pyom [G at load time"
    assert "{x" not in out, "rom {x must be converted to pyom [x at load time"
    assert "[G" in out, "pyom [G token must be present after conversion"

    ansi = miniboa_terminal.color_convert(out, "pyom", "ansi")
    assert "\033[1;32m" in ansi, "ANSI bold-green expected from {G"
    assert "\033[0m" in ansi, "ANSI reset expected from {x"
    assert "{G" not in ansi and "{x" not in ansi, "No rom tokens in final ANSI output"


@pytest.mark.skipif(
    not (_KBK_AREAS / "knightcastle.are").exists(),
    reason="run make import-kbk first — KBK area files not found",
)
def test_kbk_text_real_data_knightcastle_room_edesc_plaque():
    """Regression: knightcastle room EDESC "plaque" has {R codes.

    Verifies that room extra_descr (EDESC keyword) is now processed
    through _kbk_text in load_rooms_new.
    """
    area_file = _KBK_AREAS / "knightcastle.are"
    content = area_file.read_text(encoding="latin-1")
    # Find EDESC plaque~ followed by text up to closing ~
    m = re.search(r"EDESC\s+plaque~\s*\n(.*?)^~", content, re.MULTILINE | re.DOTALL)
    assert m is not None, "Could not find EDESC plaque in knightcastle.are"
    raw_edesc = m.group(1)
    assert "{R" in raw_edesc, "Precondition: plaque EDESC must contain {R"

    out = data_loader._kbk_text(raw_edesc)
    assert "{R" not in out, "rom {R must be converted to pyom [R at load time"
    assert "[R" in out, "pyom [R token must be present after conversion"

    ansi = miniboa_terminal.color_convert(out, "pyom", "ansi")
    assert "\033[1;31m" in ansi, "ANSI bold-red expected from {R"
    assert "{R" not in ansi, "No rom tokens in final ANSI output"


@pytest.mark.skipif(
    not (_KBK_AREAS / "knightcastle.are").exists(),
    reason="run make import-kbk first — KBK area files not found",
)
def test_kbk_text_real_data_knightcastle_object_short_descr():
    """Regression: knightcastle object short_descr 'Shield of White Roses' has {W codes.

    Verifies that object short_descr (SHORT keyword) is now processed
    through _kbk_text in load_objects_new.
    """
    area_file = _KBK_AREAS / "knightcastle.are"
    content = area_file.read_text(encoding="latin-1")
    # Find SHORT entry with 'a Shield of {WWhite{x Roses~'
    m = re.search(r"SHORT\s+a Shield of \{W[^~]*?~", content)
    assert m is not None, "Could not find object SHORT 'a Shield of {WWhite{x Roses' in knightcastle.are"
    # Extract just the descriptive text part
    m2 = re.search(r"SHORT\s+(.*?)~", m.group(0))
    assert m2 is not None, "Could not extract SHORT text"
    raw_short = m2.group(1)
    assert "{W" in raw_short, "Precondition: Shield SHORT must contain {W"

    out = data_loader._kbk_text(raw_short)
    assert "{W" not in out, "rom {W must be converted to pyom [W at load time"
    assert "[W" in out, "pyom [W token must be present after conversion"

    ansi = miniboa_terminal.color_convert(out, "pyom", "ansi")
    assert "\033[1;37m" in ansi, "ANSI bold-white expected from {W"
    assert "{W" not in ansi, "No rom tokens in final ANSI output"
