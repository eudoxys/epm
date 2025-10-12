# Eudoxys package manager

## Installation

To install the Eudoxys package manager

    python3 -m venv .venv
    . .venv/bin/activate
    pip install git+https://github.com/eudoxys/epm

## Usage

To get the index of available packages

    epm index

To get a list of installed packages

    epm list

To install a package

    epm install NAME

To upgrade a package

    epm upgrade NAME

To uninstall a package

    epm uninstall NAME

To open a package's web page

    epm open NAME

## Options

Enable debugging traceback of exceptions:

    epm --debug ...

Get the `epm` version number

    epm --version

Get help

    epm help

## Technical Guide

Packages are added to the index by including them in the [DATA](https://github.com/eudoxys/epm/blob/143eaf75be8cca8609da5d28ee9fc92e874435d1/epm/catalog.py#L12) list of the `Catalog` class.

Eudoxys repositories must include the `description` and `version` entries in the `project` section of their `pyproject.toml` file.
