"""Phase 1 acceptance test: load every area in src/area/kbk/ with zero errors."""
import logging
import pathlib

import pytest

from rom24 import data_loader, instance, settings
from rom24.content.register import register

KBK_AREAS = pathlib.Path(settings.SOURCE_DIR) / "area" / "kbk"

pytestmark = pytest.mark.skipif(
    not KBK_AREAS.exists(), reason="run make import-kbk first"
)


def test_all_kbk_areas_load(clear_instance, monkeypatch, caplog):
    # Ensure const.race_table and friends are populated before loading areas.
    register()
    monkeypatch.setattr(settings, "AREA_DIR", str(KBK_AREAS))
    monkeypatch.setattr(settings, "AREA_LIST_FILE", str(KBK_AREAS / "area.lst"))
    with caplog.at_level(logging.DEBUG, logger="rom24.data_loader"):
        data_loader.load_areas()
    assert len(instance.area_templates) >= 85
    assert len(instance.room_templates) > 7500
    assert len(instance.npc_templates) > 1800
    assert len(instance.item_templates) > 2900
    errors = [r for r in caplog.records if r.levelname == "ERROR"]
    assert errors == [], "Unexpected errors:\n" + "\n".join(
        f"  {r.name}: {r.getMessage()}" for r in errors
    )
