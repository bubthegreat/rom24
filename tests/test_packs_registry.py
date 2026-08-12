import json
import os

import pytest

from rom24 import packs


def _write_pack(root, name, manifest):
    d = os.path.join(root, name)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "pack.json"), "w") as fp:
        json.dump(manifest, fp)
    return d


def test_discover_reads_manifest(tmp_path):
    root = str(tmp_path)
    _write_pack(root, "core", {"name": "core", "version": "1.0.0", "depends": [], "data_dir": "."})
    found = packs.discover_packs(root)
    assert len(found) == 1
    p = found[0]
    assert p.name == "core"
    assert p.version == "1.0.0"
    assert p.depends == []
    assert p.data_dir == os.path.join(root, "core")


def test_discover_skips_dir_without_manifest(tmp_path):
    root = str(tmp_path)
    os.makedirs(os.path.join(root, "not_a_pack"), exist_ok=True)
    _write_pack(root, "core", {"name": "core", "version": "1.0.0"})
    found = packs.discover_packs(root)
    assert [p.name for p in found] == ["core"]


def test_discover_skips_broken_manifest(tmp_path):
    root = str(tmp_path)
    d = os.path.join(root, "broken")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "pack.json"), "w") as fp:
        fp.write("{ not valid json")
    _write_pack(root, "core", {"name": "core", "version": "1.0.0"})
    found = packs.discover_packs(root)
    assert [p.name for p in found] == ["core"]


def _pack(name, depends=None):
    return packs.Pack(name=name, path="/nonexistent/%s" % name, depends=depends or [])


def test_load_order_respects_depends():
    core = _pack("core")
    addon = _pack("necro", depends=["core"])
    order = packs.resolve_load_order([addon, core])
    assert [p.name for p in order] == ["core", "necro"]


def test_load_order_missing_dep_is_ignored():
    addon = _pack("necro", depends=["nonexistent"])
    order = packs.resolve_load_order([addon])
    assert [p.name for p in order] == ["necro"]


def test_load_order_cycle_raises():
    a = _pack("a", depends=["b"])
    b = _pack("b", depends=["a"])
    with pytest.raises(ValueError):
        packs.resolve_load_order([a, b])


def test_discover_skips_schema_invalid_manifest(tmp_path):
    root = str(tmp_path)
    # missing required "version"
    _write_pack(root, "bad", {"name": "bad"})
    _write_pack(root, "good", {"name": "good", "version": "1.0.0"})
    found = packs.discover_packs(root)
    assert [p.name for p in found] == ["good"]


def test_discover_skips_wrong_typed_field(tmp_path):
    root = str(tmp_path)
    # depends must be an array of strings
    _write_pack(root, "bad2", {"name": "bad2", "version": "1.0", "depends": "core"})
    found = packs.discover_packs(root)
    assert found == []
