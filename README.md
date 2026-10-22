[![Deploy Pages](https://github.com/eudoxys/epm/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/eudoxys/epm/actions/workflows/deploy-pages.yml)

# Eudoxys product manager

For documentation see https://www.eudoxys.com/epm.

## Installation

To install the Eudoxys product manager

    python3 -m venv .venv
    . .venv/bin/activate
    pip install git+https://github.com/eudoxys/epm

## Usage

To get the index of available products

    epm index

To get a list of repository names (not a list of locally installed packages)

    epm list

An optional regular expression filters those names, for example `epm list '^epm$'`.

To install a product

    epm install NAME

To upgrade a product

    epm upgrade NAME

To uninstall a product

    epm uninstall NAME

To open a product's web page

    epm help NAME

Without a product name, `epm help` opens EPM's own page. All commands can also be
run as `python -m epm`, for example `python -m epm --help`.

## Options

Enable debugging traceback of exceptions:

    epm --debug ...

Get the `epm` version number

    epm --version

Get help

    epm --help

## Technical Guide

By default, [Catalog](https://github.com/eudoxys/epm/blob/main/epm/catalog.py)
discovers products by scanning the Eudoxys organization's GitHub repositories:
`Catalog.LIST = None` enables discovery rather than supplying an explicit list.
The `list` command prints repository names, while `index` reads each repository's
`pyproject.toml` from its `main` branch to display product metadata.

Eudoxys repositories should include the `description` and `version` entries in the
`project` section of their `pyproject.toml` file. Including `eudoxys` in the
project's `keywords` adds the `E` flag in the index; it does not filter the `list`
command's output.

Product types include the following flags:

- 'M' a module is included in the product
- 'P' packages are include in the product
- 'C' a command line interface (CLI) is included in the product
- 'E' product is an official Eudoxys release
