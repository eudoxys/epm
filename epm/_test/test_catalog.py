"""Tests for `epm.catalog`"""

import pytest

from epm.catalog import Catalog

def test_index_all(catalog): # pylint: disable=unused-argument
    assert Catalog().index == ["released","unreleased","noproject"]

def test_index_pattern(catalog): # pylint: disable=unused-argument
    assert Catalog("un").index == ["unreleased"]
    assert Catalog(["rel","no"]).index == ["released","noproject"]
    assert not Catalog("missing").index

def test_repository(catalog): # pylint: disable=unused-argument
    assert Catalog().repository("released") == "https://github.com/eudoxys/released"
    with pytest.raises(AssertionError):
        Catalog("released").repository("unreleased")

def _table(catalog_obj,**kwargs):
    lines = []
    catalog_obj.print(print=lines.append,**kwargs)
    return lines

def test_print_released_only(catalog): # pylint: disable=unused-argument
    lines = _table(Catalog())
    assert lines[0].split() == ["Product","Version","Type","Description"]
    assert set(lines[1]) == {"-"," "}
    assert len(lines) == 3
    assert lines[2].split()[:3] == ["released","1.2.3","MPCE"]
    assert lines[2].endswith("A released package")

def test_print_all(catalog): # pylint: disable=unused-argument
    lines = _table(Catalog(),all=True)
    rows = {x.split()[0]:x.split() for x in lines[2:]}
    assert set(rows) == {"released","unreleased"} # no pyproject.toml -> omitted
    assert rows["unreleased"][2] == "M---"
