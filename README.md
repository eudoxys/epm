# Eudoxys product manager

## Installation

To install the Eudoxys product manager

    python3 -m venv .venv
    . .venv/bin/activate
    pip install git+https://github.com/eudoxys/epm

## Usage

To get the index of available products

    epm index

To get a list of installed products

    epm list

To install a product

    epm install NAME

To upgrade a product

    epm upgrade NAME

To uninstall a product

    epm uninstall NAME

To open a product's web page

    epm open NAME

## Options

Enable debugging traceback of exceptions:

    epm --debug ...

Get the `epm` version number

    epm --version

Get help

    epm help

## Technical Guide

Products are added to the index by including them in the [LIST](https://github.com/eudoxys/epm/blob/main/epm/catalog.py#L16) list of the `Catalog` class.

Eudoxys repositories must include the `description` and `version` entries in the `project` section of their `pyproject.toml` file. In addition, the 'keywords' must include `eudoxys` for the product to appear in the `list` command output.

Product types include the following flags:

- 'M' a module is included in the product
- 'P' packages are include in the product
- 'C' a command line interface (CLI) is included in the product
- 'E' product is an official Eudoxys release
