Testing
-------

From the repository root:

	python3 -m venv .venv
	. .venv/bin/activate
	python3 -m pip install --upgrade pip
	pip install -e . pytest
	pytest

No credentials are needed. The `network` tests query the GitHub API, which
allows 60 unauthenticated requests per hour; to raise the limit put a GitHub
token in `~/.github/access-token` (CI writes the workflow's `GITHUB_TOKEN`
there). Skip them with:

	pytest -m "not network"

The full suite takes a few seconds.

`conftest.py`
-------------

Provides the `catalog` fixture, which replaces the GitHub scan and the
`pyproject.toml` downloads with three synthetic repositories (released,
unreleased, and one without a `pyproject.toml`).

`test_catalog.py`
-----------------

Fast. Checks `epm.catalog.Catalog` pattern matching, repository URLs, the
release filter, the `Type` flags, and the `print` table layout.

	pytest epm/_test/test_catalog.py

`test_cli.py`
-------------

Fast. Checks every `epm` command and exit code, with `pip` replaced by a stub
that records the commands it would run.

	pytest epm/_test/test_cli.py

`test_network.py`
-----------------

Networked (`network` marker). Scans the real `eudoxys` organization and reads
this repository's `pyproject.toml` from `main`.

	pytest epm/_test/test_network.py
