[![Validation](https://github.com/eudoxys/epm/actions/workflows/validate.yaml/badge.svg)](https://github.com/eudoxys/epm/actions/workflows/validate.yaml)
[![Documentation](https://github.com/eudoxys/epm/actions/workflows/deploy-pages.yaml/badge.svg)](https://github.com/eudoxys/epm/actions/workflows/deploy-pages.yaml)

Eudoxys Package Manager

`epm` finds, installs, upgrades, and removes the Python packages published
in the [eudoxys](https://github.com/eudoxys) GitHub organization. It scans the
organization's repositories, reads each one's `pyproject.toml` from `main`,
and runs `pip install git+https://github.com/eudoxys/NAME` for you.

# Documentation

See https://www.eudoxys.com/epm

# Installation

    python3 -m venv .venv
    . .venv/bin/activate
    pip install --upgrade git+https://github.com/eudoxys/epm

`epm` requires Python 3.11 or later.

# Usage

Get the index of available packages (add `--all` to include unreleased ones)

    epm index

List the installed Eudoxys packages

    epm list

Install, upgrade, or uninstall a package

    epm install NAME
    epm upgrade NAME
    epm uninstall NAME

Open a package's GitHub page

    epm help NAME

Other options

    epm --help       # command help
    epm --version    # epm version number
    epm --debug ...  # debug logging and traceback on exceptions

# Publishing a package to `epm`

`epm` lists every repository in the organization that has a `pyproject.toml`.
For a package to appear in `epm index`, its `[project]` section must have a
`description` and a `version` greater than `0.0.0`; include `eudoxys` in
`keywords` to flag it as an official Eudoxys release. See
[Package types](https://www.eudoxys.com/epm#package-types) for the `Type`
column flags.

# Maintenance

## Update docs

    make docs

## Run tests

    pip install -e . pytest
    pytest

The tests marked `network` query the GitHub API; skip them with
`pytest -m "not network"`. See [`epm/_test/README.md`](epm/_test/README.md).

# Examples

## Command line

    epm index epm

outputs

    Product Version Type Description
    ------- ------- ---- -----------------------
    epm     26.10.0 MPCE Eudoxys Package Manager

## Python

    from epm import Catalog
    Catalog("epm").print()
