from tools.kbk_import.resolve import Resolver

R = Resolver({"ALIGN_ANY": "3", "A": "1", "H": "128", "M": "4096", "V": "2097152",
              "AFF_INFRARED": "(H)", "CLASS_FIGHTER": "0", "MSL": "(2*4096)"})


def test_plain_and_define():
    assert R.num("0") == 0
    assert R.num("-10") == -10
    assert R.num("ALIGN_ANY") == 3
    assert R.num("MSL") == 8192


def test_or_expression():
    assert R.num("A | H | M | V") == 1 | 128 | 4096 | 2097152


def test_special_forms():
    assert R.slot("SLOT(551)") == 551
    assert R.gsn_name("&gsn_absorb") == "absorb"
    assert R.gsn_name("NULL") is None
    assert R.spell_name("spell_acid_blast") == "acid blast"
    assert R.spell_name("spell_null") is None
    assert R.spell_name("NULL") is None
    assert R.spell_name("0") is None


def test_bools_and_strings():
    assert R.value("TRUE") is True
    assert R.value("FALSE") is False
    assert R.value(("str", "class basics")) == "class basics"


def test_chained_define_also_appearing_independently():
    r = Resolver({"A": "B | 1", "B": "2"})
    # must resolve regardless of substitution order
    for _ in range(20):
        assert r.num("A | B") == 3


def test_circular_define_raises_instead_of_hanging():
    import pytest
    r = Resolver({"A": "(A | 1)"})
    with pytest.raises(ValueError):
        r.num("A")
    r2 = Resolver({"A": "B | 1", "B": "A | 2"})
    with pytest.raises(ValueError):
        r2.num("A")
