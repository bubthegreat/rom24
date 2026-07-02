"""Shared pytest fixtures for rom24 test suite."""
import pytest

from rom24 import instance


@pytest.fixture
def clear_instance():
    """Reset all instance-level global state so each full-boot test starts fresh.

    Both test_boot_kbk and test_kbk_full_load call data_loader.load_areas() which
    appends to these dicts; running them in the same session without clearing first
    would cause duplicate-vnum ERRORs and false assertion failures.
    """
    instance.area_templates.clear()
    instance.room_templates.clear()
    instance.npc_templates.clear()
    instance.item_templates.clear()
    instance.shop_templates.clear()
    instance.global_instances.clear()
    instance.areas.clear()
    instance.rooms.clear()
    instance.npcs.clear()
    instance.items.clear()
    instance.shops.clear()
    instance.instances_by_room.clear()
    instance.instances_by_area.clear()
    instance.instances_by_item.clear()
    instance.instances_by_npc.clear()
    instance.instances_by_shop.clear()
    instance.not_to_instance.clear()
    yield
    # Post-test teardown: leave state cleared so subsequent tests start fresh.
    instance.area_templates.clear()
    instance.room_templates.clear()
    instance.npc_templates.clear()
    instance.item_templates.clear()
    instance.shop_templates.clear()
    instance.global_instances.clear()
    instance.areas.clear()
    instance.rooms.clear()
    instance.npcs.clear()
    instance.items.clear()
    instance.shops.clear()
    instance.instances_by_room.clear()
    instance.instances_by_area.clear()
    instance.instances_by_item.clear()
    instance.instances_by_npc.clear()
    instance.instances_by_shop.clear()
    instance.not_to_instance.clear()
