"""Tier 2: shopkeeping — list, buy, sell.

Selling was fully broken (a string item_type compared against a shop's numeric
buy_type always scored 0, plus a nonexistent ``item.sell_extract`` attribute,
``item.get()`` called with no arg, and a broken ``obj_to_keeper``). These lock
the buy/sell/list loop in the Midgaard general store (room 3010, the grocer).
"""
from helpers import make_pc, spawn_item, run
from rom24 import merc


def test_list_shows_stock(booted_world):
    """'list' shows items the keeper has for sale."""
    pc = make_pc(name="Browser", room_vnum=3010)
    out = run(pc, "list")
    assert "torch" in out.lower(), "list did not show the grocer's stock: %r" % out[:120]


def test_buy_adds_item_deducts_coin(booted_world):
    """'buy' gives the player the item and takes coin."""
    pc = make_pc(name="Purchaser", room_vnum=3010)
    pc.gold = 100
    pc.silver = 100
    wealth0 = pc.gold * 100 + pc.silver
    count0 = len(list(pc.inventory))
    run(pc, "buy torch")
    assert len(list(pc.inventory)) == count0 + 1, "buy did not add the item"
    assert pc.gold * 100 + pc.silver < wealth0, "buy did not deduct any coin"


def test_sell_pays_coin_removes_item(booted_world):
    """'sell' pays the player and takes the item away (the fixed path)."""
    pc = make_pc(name="Vendor", room_vnum=3010)
    pc.gold = 0
    pc.silver = 0
    lantern = spawn_item(3031, pc)        # a hooded brass lantern (worth > 0)
    lid = lantern.instance_id
    out = run(pc, "sell lantern")
    assert "you sell" in out.lower(), "sell did not complete: %r" % out
    assert pc.gold * 100 + pc.silver > 0, "sell paid nothing"
    assert lid not in pc.inventory, "sold lantern still in inventory"
