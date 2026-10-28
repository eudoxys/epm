"""Eudoxys Package Manager

Syntax
------

    epm COMMAND [NAME ...] [-h] [-a] [-d] [-v] [-w]

Positional arguments
--------------------

  - `COMMAND`: one of

    - `checkup [PATTERN ...]`: output the installed Eudoxys packages that are
      older than the version on `main` (nothing when all are up to date)

    - `help [NAME ...]`: open the GitHub page of each package (default `epm`)

    - `index [PATTERN ...]`: output the table of available packages

    - `install PATTERN [...]`: install the packages matching each pattern

    - `list [PATTERN ...]`: output the installed Eudoxys packages and versions

    - `uninstall NAME [...]`: uninstall packages

    - `upgrade PATTERN [...]`: upgrade the packages matching each pattern

  - `NAME`/`PATTERN`: package name, or a regular expression matched against
    the start of package names

Optional arguments
------------------

  - `-a|--all`: `index` includes unreleased packages (version `0.0.0`)

  - `-d|--debug`: enable debug logging and traceback on exceptions

  - `-h|--help`: show this help message and exit

  - `-v|--version`: output the `epm` version number and exit

  - `-w|--warning`: enable warning messages from python

Description
-----------

`epm` finds, installs, and upgrades the Python packages published in the
[eudoxys](https://github.com/eudoxys) GitHub organization. Packages are
installed with `pip install git+https://github.com/eudoxys/NAME`, i.e., from
the head of each repository's `main` branch.

Given the organization's repositories, `epm.Catalog` builds an index that is
expected to satisfy:

  1. **Coverage.** Every repository in the organization is in `Catalog.LIST`
     (or, if `Catalog.LIST` is set, exactly that list).

  2. **Metadata.** `Catalog.metadata(NAME)` returns the parsed
     `pyproject.toml` of the repository's `main` branch, or `None` if it has
     none. Repositories without one are omitted from `epm index`.

  3. **Release filter.** `epm index` lists only packages whose `[project]
     version` is greater than `0.0.0`, unless `--all` is given.

Package types
-------------

The `Type` column of `epm index` has four flags (`-` when absent):

  - `M`: Eudoxys managed package (has a `pyproject.toml`)

  - `P`: `[tool.setuptools] packages` is set

  - `C`: `[project.scripts]` defines a command line interface

  - `E`: `[project] keywords` includes `eudoxys` (official Eudoxys release)

Exit codes
----------

  - `0`: success

  - `1`: invalid command line

  - `2`: one or more `pip` commands failed

  - `3`: no package matches a name

  - `9`: unexpected exception (use `--debug` for the traceback)

What is not promised
--------------------

  - Packages are installed from `main`, not from tagged releases, and `epm`
    does not resolve or pin versions between Eudoxys packages; `pip` does.

  - `pip` runs in the interpreter that runs `epm`; `epm` does not create or
    select virtual environments.

  - The catalog depends on the GitHub API, which rate-limits unauthenticated
    requests (see `epm.catalog`).

```mermaid
flowchart LR
    github[(GitHub eudoxys org)] --> Catalog --> index[epm index]
    Catalog --> pip[pip install git+...] --> env[(Python environment)]
```
"""

try:
    import importlib.metadata
    __version__ = importlib.metadata.version("eudoxys")
except Exception: # pylint: disable=broad-exception-caught
    __version__ = "dev"

from epm.catalog import Catalog, CatalogError
from epm.cli import main
