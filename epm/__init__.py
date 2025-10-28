"""Eudoxys product manager

Syntax: epm [OPTIONS ...] COMMAND [ARGUMENTS ...]

Options:

    --debug: enable traceback of exceptions

    -h|--help: output this help

    -v|--version: output the EPM version number

Commands:

    help [PACKAGE ...]: open help on packages

    index [PATTERN [...]]: output list of available packages

    install NAME [...]: install packages

    list [PATTERN [...]]: output list of installed packages

    uninstall NAME [...]: uninstall packages

    upgrade NAME [...]: upgrade packages
"""

import os
import sys
import re
import importlib.metadata
import warnings
import webbrowser
try:
    from .catalog import Catalog
except ImportError:
    from catalog import Catalog
try:
    __version__ = importlib.metadata.version('epm')
except importlib.metadata.PackageNotFoundError:
    __version__ = "dev"

DEBUG=False

def list(pattern:str=None) -> list[list[str]]:
    """Get list of installed Eudoxys packages"""
    result = []
    for product in importlib.metadata.distributions():
        name = product.name
        if not pattern or re.match(pattern,name):
            info = importlib.metadata.distribution(product.name).metadata
            warnings.filterwarnings("error")
            try:
                keywords = info["Keywords"]
            except (KeyError,DeprecationWarning):
                keywords = None
            warnings.resetwarnings()
            if "eudoxys" in str(keywords).split(","):
                result.append(name)

    return result

def main(
    args:list=sys.argv[1:],
    stdout:callable=lambda x: print(x,file=sys.stdout),
    stderr:callable=lambda x: print(x if x.startswith("Syntax: ") else f"ERROR [epm]: {x}",file=sys.stderr),
    exceptions:list=None
    ):
    """Main routine"""

    global DEBUG

    E_OK = 0
    E_SYNTAX = 1
    E_FAILED = 2
    E_NOTFOUND = 3
    E_EXCEPTION = 9

    try:

        if len(args) == 0:

            stderr("\n".join([x for x in __doc__.split("\n") if x.startswith("Syntax: ")]))
            return E_SYNTAX

        #
        # Options
        #

        if args[0] in ["--debug"]:

            DEBUG = True
            del args[0]

        if args[0] in ["-h","--help"]:

            stdout(__doc__)
            return E_OK

        if args[0] in ["-v","--version"]:

            stdout(__version__)
            return E_OK

        #
        # Commands
        #

        # help - open product webpage
        if args[0] == "help":

            for arg in args[1:] if len(args) > 1 else ["epm"]:

                if not arg in Catalog.LIST:
                    stderr(f"'{arg}' is not a valid Eudoxys product")
                else:
                    url = os.path.join(Catalog.REPO,arg)
                    webbrowser.open(url,new=1,autoraise=True)

            return E_OK

        # list - get list of installed packages
        elif args[0] == "list":

            catalog = Catalog(list())
            catalog.print(print=stdout)
            return E_OK

        # index - get list of available packages
        elif args[0] == "index":

            catalog = Catalog()
            catalog.print(print=stdout)
            return E_OK

        # install - install packages
        elif args[0] == "install" and len(args) > 1:

            errors = 0
            for arg in args[1:]:
                catalog = Catalog(arg)
                if not catalog.index:
                    stderr(f"no packages match '{arg}'")
                    return E_NOTFOUND
                for product in catalog.index:
                    code = os.system(f"pip install git+{catalog.repository(product)}")
                    if code != 0:
                        stderr(f"'{product}' install failed --> error code {code}")
                        errors += 1
            return E_OK if not errors else E_FAILED

        # uninstall - uninstall packages
        elif args[0] == "uninstall" and len(args) > 1:

            errors = 0
            for arg in args[1:]:
                if arg in list():
                    code = os.system(f"pip uninstall -y {arg}")
                    if code != 0:
                        stderr(f"'{arg}' uninstall failed --> error code {code}")
                        errors != 1
            return E_OK if not errors else E_FAILED

        # upgrade - upgrade packages
        elif args[0] == "upgrade" and len(args) > 1:

            errors = 0
            for arg in args[1:]:
                catalog = Catalog(arg)
                if not catalog.index:
                    stderr(f"no packages match '{arg}'")
                    return E_NOTFOUND
                for product in catalog.index:
                    code = os.system(f"pip install --upgrade git+{catalog.repository(product)}")
                    if code != 0:
                        stderr(f"'{product}' install failed --> error code {code}")
                        errors += 1
            return E_OK if not errors else E_FAILED

        raise ValueError(f"'{args[0]}' is an invalid command")

    except:
        if DEBUG:
            raise
        e_type,e_value,e_trace = sys.exc_info()
        if e_type in exceptions if exceptions else []:
            raise
        stderr(f"{e_type.__name__} {e_value}")
        return E_EXCEPTION

if __name__ == "__main__":

    main(['index'])
