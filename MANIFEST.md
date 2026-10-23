# MANIFEST

Map of the `eudoxys/epm` repository. Every tracked file is covered by
one row or glob below; check with `python .github/check_manifest.py`.
Update this file in the same PR that adds, moves, or deletes a file.

## Start here

1. `CLAUDE.md` — conventions and working rules
2. `epm/__init__.py` — package docs (CLI syntax, package rules) and public API
3. `epm/cli.py` — commands
4. `epm/catalog.py` — GitHub scan and `pyproject.toml` metadata

## Task index

- Add a CLI command or option: `epm/cli.py` (`COMMANDS`, `_COMMANDS`), `epm/__init__.py` Syntax section, `README.md`; test in `epm/_test/test_cli.py`
- Change the index table or type flags: `epm/catalog.py` `Catalog.print`, `epm/__init__.py` Package types, `README.md`; test in `epm/_test/test_catalog.py`
- Change how packages are found: `epm/catalog.py` `Catalog.scanrepos`; test in `epm/_test/test_network.py`
- Fix a test: `epm/_test/conftest.py` holds the synthetic catalog
- Update docs: docstrings, then `make docs`
- Release: `pyproject.toml` version; see the eudoxys-package skill checklist

## Package

| Path | Purpose | Notes |
|---|---|---|
| `epm/__init__.py` | package docs, re-exports | pdoc landing page |
| `epm/cli.py` | CLI `main()` | entry point `epm`; tested by `_test/test_cli.py` |
| `epm/catalog.py` | `Catalog`, `CatalogError` | tested by `_test/test_catalog.py`, `_test/test_network.py` |
| `epm/.gitignore` | generated-output ignores | |

## Tests

| Path | Purpose | Notes |
|---|---|---|
| `epm/_test/README.md` | how to run tests | |
| `epm/_test/conftest.py` | synthetic `catalog` fixture | no network |
| `epm/_test/test_catalog.py` | `epm.catalog` tests | fast |
| `epm/_test/test_cli.py` | `epm.cli` tests | fast; `pip` stubbed |
| `epm/_test/test_network.py` | live GitHub scan | marked `network` |

## Repository

| Path | Purpose | Notes |
|---|---|---|
| `README.md` | user overview | |
| `CLAUDE.md` | assistant guidance | |
| `MANIFEST.md` | this file | |
| `CONTRIBUTING.md` | contributor guide | approved-issue rule |
| `TODO.md` | roadmap | |
| `pyproject.toml` | packaging | version here |
| `requirements.txt` | dependencies | |
| `Makefile` | `make docs`, `make test` | |
| `LICENSE` | MIT | |
| `.gitignore` | | GitHub Python template |
| `.gitattributes` | | `* text=auto` |
| `.github/workflows/*.yaml` | CI: tests, docs, approved-issue check | |
| `.github/check_manifest.py` | checks this file | run in `validate.yaml` |

## Don't read

`docs/` (generated), `.venv/`, `build/`, `*.egg-info/`.
