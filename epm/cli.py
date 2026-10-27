"""Command line interface

See `epm` for the command syntax.

Examples
--------

    epm index epm

outputs

    Product Version Type Description
    ------- ------- ---- -----------------------
    epm     26.10.0 MPCE Eudoxys Package Manager

(versions and descriptions are read from each repository's `main` branch at
run time, so they change as packages are released).

Caveats
-------

  - `install`, `upgrade`, and `uninstall` run `pip` with the same Python
    interpreter that runs `epm`, so packages go into the environment `epm`
    is installed in.
"""

import sys
import argparse
import logging
import warnings
import webbrowser
import subprocess
import importlib.metadata

from epm.catalog import Catalog

_logger = logging.getLogger(__file__)

E_OK = 0
"""Exit code: success"""

E_SYNTAX = 1
"""Exit code: invalid command line"""

E_FAILED = 2
"""Exit code: one or more `pip` commands failed"""

E_NOTFOUND = 3
"""Exit code: no catalog package matches a name"""

E_EXCEPTION = 9
"""Exit code: unexpected exception (use `--debug` for the traceback)"""

COMMANDS = ["help","index","install","list","uninstall","upgrade"]
"""Valid commands"""

def _version() -> str:
    try:
        return importlib.metadata.version("eudoxys")
    except Exception: # pylint: disable=broad-exception-caught
        return "dev"

def _installed() -> dict[str,str]:
    """Installed distributions as `{name: version}` (names lowercase)"""
    result = {}
    for dist in importlib.metadata.distributions():
        name = dist.metadata["Name"]
        if name:
            result[name.lower()] = dist.version
    return result

def _pip(*args:str) -> int:
    """Run pip in the interpreter running epm and return its exit code"""
    command = [sys.executable,"-m","pip",*args]
    _logger.debug("running %s",command)
    return subprocess.run(command,check=False).returncode

def _error(msg:str) -> None:
    print(f"ERROR [epm]: {msg}",file=sys.stderr)

def main(argv:list[str]|None=None) -> int:
    """Command line entry point

    Arguments
    ---------

      - `argv`: command line arguments (default `sys.argv[1:]`)

    Returns
    -------

      - `int`: exit code (see `E_OK`, `E_SYNTAX`, `E_FAILED`, `E_NOTFOUND`,
        `E_EXCEPTION`)
    """
    parser = argparse.ArgumentParser(prog="epm",
        description="Eudoxys Package Manager",
        epilog="See https://www.eudoxys.com/epm for full documentation.")
    parser.add_argument("command",choices=COMMANDS,
        help="command to run (see https://www.eudoxys.com/epm)")
    parser.add_argument("names",nargs="*",metavar="NAME",
        help="package names (regular expressions for index, install, upgrade, and list)")
    parser.add_argument("-a","--all",action="store_true",
        help="index: include unreleased packages (version 0.0.0)")
    parser.add_argument("-d","--debug",action="store_true",
        help="enable debug logging and traceback on exceptions")
    parser.add_argument("-v","--version",action="version",version=_version(),
        help="show the epm version number and exit")
    parser.add_argument("-w","--warning",action="store_true",
        help="enable warning messages from python")
    try:
        # intermixed: Python 3.11 rejects NAMEs after an option (e.g. `index -a NAME`)
        args = parser.parse_intermixed_args(argv)
    except SystemExit as err:
        return E_OK if err.code in (0,None) else E_SYNTAX

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.WARNING)
    if not args.warning:
        warnings.simplefilter("ignore")

    try:
        return _COMMANDS[args.command](args)
    except Exception as err: # pylint: disable=broad-exception-caught
        if args.debug:
            raise
        _error(f"{type(err).__name__} {err}")
        return E_EXCEPTION

def _help(args:argparse.Namespace) -> int:
    catalog = Catalog()
    for name in args.names or ["epm"]:
        if name not in catalog.LIST:
            _error(f"'{name}' is not a valid Eudoxys package")
        else:
            webbrowser.open(f"{Catalog.REPO}/{name}",new=1,autoraise=True)
    return E_OK

def _index(args:argparse.Namespace) -> int:
    Catalog(args.names or None).print(all=args.all)
    return E_OK

def _list(args:argparse.Namespace) -> int:
    installed = _installed()
    catalog = Catalog(args.names or None)
    for name in sorted(x for x in catalog.index if x.lower() in installed):
        print(f"{name} {installed[name.lower()]}")
    return E_OK

def _install(args:argparse.Namespace,upgrade:bool=False) -> int:
    if not args.names:
        _error(f"{args.command} requires at least one NAME")
        return E_SYNTAX
    errors = 0
    for name in args.names:
        catalog = Catalog(name)
        if not catalog.index:
            _error(f"no packages match '{name}'")
            return E_NOTFOUND
        for package in catalog.index:
            options = ["install","--upgrade"] if upgrade else ["install"]
            code = _pip(*options,f"git+{catalog.repository(package)}")
            if code != 0:
                _error(f"'{package}' {args.command} failed --> error code {code}")
                errors += 1
    return E_OK if not errors else E_FAILED

def _upgrade(args:argparse.Namespace) -> int:
    return _install(args,upgrade=True)

def _uninstall(args:argparse.Namespace) -> int:
    if not args.names:
        _error("uninstall requires at least one NAME")
        return E_SYNTAX
    installed = _installed()
    catalog = Catalog()
    errors = 0
    for name in args.names:
        if name not in catalog.LIST:
            _error(f"'{name}' is not a valid Eudoxys package")
            errors += 1
        elif name.lower() not in installed:
            _error(f"'{name}' is not installed")
            errors += 1
        else:
            code = _pip("uninstall","-y",name)
            if code != 0:
                _error(f"'{name}' uninstall failed --> error code {code}")
                errors += 1
    return E_OK if not errors else E_FAILED

_COMMANDS = {
    "help": _help,
    "index": _index,
    "install": _install,
    "list": _list,
    "uninstall": _uninstall,
    "upgrade": _upgrade,
}

if __name__ == "__main__":
    sys.exit(main())
