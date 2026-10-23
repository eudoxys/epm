# CLAUDE.md

Guidance for Claude when working in the `eudoxys/epm` repository.
General Eudoxys package conventions are in the `eudoxys-package` skill
(github.com/eudoxys/claude); this file records only what is specific to `epm`.

## What this is

`epm`, the Eudoxys Package Manager: a small CLI that lists the repositories
of the `eudoxys` GitHub organization, reads each one's `pyproject.toml` from
`main`, and installs/upgrades/uninstalls them with `pip install git+...`.
Python 3.11+ (uses `tomllib`), alpha. No sibling Eudoxys dependencies; only
`requests`.

- Docs site: https://www.eudoxys.com/epm (pdoc from docstrings)
- Maintainer: David P. Chassin
- CLI entry point: `epm` -> `epm.cli:main`

## Where things are

- `MANIFEST.md`: map of every file, a task index, and what not to read.
  Read it first instead of listing folders.
- No `DESIGN.md`: the design fits in the package docstring (`epm/__init__.py`).

## Core conventions

- `epm.catalog.Catalog` holds class-level settings (`REPO`, `DATA`, `LIST`,
  `CACHEFILE`, `ACCESS_TOKEN`); tests set `Catalog.LIST` and patch
  `Catalog.metadata` instead of calling GitHub.
- `epm` itself defines what other Eudoxys packages must put in their
  `pyproject.toml` (description, version > `0.0.0`, `eudoxys` keyword,
  `[project.scripts]`). If you change those rules, update the package
  docstring, `README.md`, and the `eudoxys-package` skill together.
- CLI commands are functions `_<command>(args) -> int` registered in
  `epm.cli._COMMANDS`; exit codes are the `E_*` constants in `epm.cli`.
- `pip` is run through `epm.cli._pip`, using `sys.executable -m pip`.

## Style

No spaces after commas in argument lists and calls; 4-space indent.

## Build, test, docs

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install --upgrade pip && pip install -e . pytest
pytest                   # all tests; network tests call the GitHub API
pytest -m "not network"  # offline
make docs
```

CI (`validate.yaml`) runs pylint (informational) and pytest on 3.11–3.13.

`publish-pypi.yaml` builds and uploads to PyPI when a tag `vX.Y.Z` is
pushed; it fails unless the tag equals `v` + `[project] version`. It uses
PyPI trusted publishing through the GitHub `pypi` environment (no token).

## Known rough edges (don't "fix" silently; mention or ask)

- Version filtering in `Catalog.print` compares strings (`"0.10.0" > "0.0.0"`
  works, but ordering between real versions would not).
- `Catalog` builds URLs with `os.path.join`, which would use `\` on Windows.
- Every `Catalog()` rescans the organization (one GitHub API request per 100
  repos, plus one `pyproject.toml` download per package for `index`);
  `CACHEFILE` is off by default.
- The `Makefile` uses `source`, which `/bin/sh` on Debian/Ubuntu (dash)
  lacks, so `make docs` falls back to the system `pip` there.
- The `P` type flag reflects only `[tool.setuptools] packages`.

## Working rules

- Never commit `docs/` (generated) or `.venv/`; `epm/.gitignore` ignores a
  local catalog cache file.
- When a command, option, or output column changes, update the
  `epm/__init__.py` docstring, the `epm/cli.py` example, and `README.md`.
- Update `MANIFEST.md` when adding, moving, or deleting files, and run
  `python .github/check_manifest.py`.
- Tests must not install or uninstall anything: stub `epm.cli._pip`.
