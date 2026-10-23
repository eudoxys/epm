"""Networked tests: query the real eudoxys GitHub organization

These are rate-limited by GitHub when unauthenticated (see `epm.catalog`).
"""

import pytest

from epm.catalog import Catalog

pytestmark = pytest.mark.network

def test_scan_finds_epm(monkeypatch):
    monkeypatch.setattr(Catalog,"LIST",None)
    assert "epm" in Catalog().index

def test_epm_metadata(monkeypatch):
    monkeypatch.setattr(Catalog,"LIST",["epm"])
    info = Catalog("epm").metadata("epm")
    assert info["project"]["name"] == "epm"
    assert "eudoxys" in info["project"]["keywords"]
    assert "epm" in info["project"]["scripts"]
