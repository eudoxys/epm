"""Shared test setup

Fast tests use the `catalog` fixture, which replaces the GitHub scan and the
`pyproject.toml` downloads with synthetic data, so they need no network.
"""

import pytest

from epm.catalog import Catalog

PROJECTS = {
    "released": {
        "project": {
            "name": "released",
            "version": "1.2.3",
            "description": "A released package\nsecond line",
            "keywords": ["eudoxys"],
            "scripts": {"released": "released.cli:main"},
            },
        "tool": {"setuptools": {"packages": ["released"]}},
        },
    "unreleased": {
        "project": {
            "name": "unreleased",
            "version": "0.0.0",
            "description": "Not yet released",
            },
        },
    "noproject": None,
}
"""Synthetic `pyproject.toml` contents by repository name"""

@pytest.fixture
def catalog(monkeypatch):
    """Catalog of synthetic repositories (no network)"""
    monkeypatch.setattr(Catalog,"LIST",list(PROJECTS))
    monkeypatch.setattr(Catalog,"metadata",lambda self,product: PROJECTS[product])
    return Catalog
