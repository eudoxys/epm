"""Eudoxys package manager

Syntax: epm [OPTIONS ...] COMMAND [ARGUMENTS ...]

Options:

    -h|--help: get this help

    -v|--version: get the EPM version number

Commands:

    help: get this help

    index: get list of available packages

    list: get list of installed packages
"""

import os
import sys
import re
import importlib.metadata
import warnings
try:
    from .catalog import Catalog
except ImportError:
    from catalog import Catalog
try:
    __version__ = importlib.metadata.version('epm')
except importlib.metadata.PackageNotFoundError:
    __version__ = "dev"

def list(pattern:str=None) -> list[list[str]]:

    result = []
    for package in importlib.metadata.distributions():
        name = package.name
        if not pattern or re.match(pattern,name):
            info = importlib.metadata.distribution(package.name).metadata
            try:
                warnings.filterwarnings("error")
                keywords = info["Keywords"]
                warnings.resetwarnings()
            except (KeyError, DeprecationWarning):
                keywords = None
            if "eudoxys" in str(keywords).split(","):
                description = " / ".join([x for x in info['Description'].split("\n") if x and not x.startswith("#")])
                version = info["Version"]
                result.append([name,version,description])

    return result


def main(
    args:list=sys.argv[1:],
    stdout:callable=lambda x: print(x,file=sys.stdout),
    stderr:callable=lambda x: print(x if x.startswith("Syntax: ") else f"ERROR [epm]: {x}",file=sys.stderr),
    exceptions:list=None
    ):

    try:
        E_OK = 0
        E_SYNTAX = 1
        E_FAILED = 2
        E_NOTFOUND = 3
        E_EXCEPTION = 9

        if len(args) == 0:

            stderr("\n".join([x for x in __doc__.split("\n") if x.startswith("Syntax: ")]))
            return E_SYNTAX

        #
        # Options
        #

        if args[0] in ["-h","--help","help"]:

            stdout(__doc__)
            return E_OK

        if args[0] in ["-v","--version"]:

            stdout(__version__)
            return E_OK

        #
        # Commands
        #

        # list - get list of installed packages
        if args[0] == "list":

            stdout(list())
            return E_OK

        # index - get list of available packages
        if args[0] == "index":

            catalog = Catalog()
            if catalog.index:
                result = {}
                header = ["package","version","description"]
                underline = {x:len(x) for x in header}
                for package in catalog.index:
                    info = Catalog().metadata(package)
                    import json
                    try:
                        description = info["project"]["description"]
                    except KeyError:
                        description = ""
                    try:
                        version = info["project"]["version"]
                    except KeyError:
                        version = ""
                    result[package] = {x:eval(x) for x in header}
                    underline = {x:max(underline[x],len(eval(x))) for x in header}
                print(" ".join([x.title()+" "*(underline[x]-len(x)) for x in header]))
                print(" ".join(['-'*underline[x] for x in header]))
                for package,info in result.items():
                    print(" ".join([y+" "*(underline[x]-len(y)) for x,y in info.items()]))
            return E_OK

        # install - install packages
        if args[0] == "install" and len(args) > 1:

            catalog = Catalog(args[1])
            if not catalog.index:
                stderr(f"no packages match '{args[1]}'")
                return E_NOTFOUND
            errors = 0
            for package in catalog.index:
                code = os.system(f"pip install git+{catalog.repository(package)}")
                if code != 0:
                    stderr(f"'{package}' install failed --> error code {code}")
                    errors += 1
            return E_OK if not errors else E_FAILED



        # uninstall - uninstall packages

        # upgrade - upgrade packages

        # open - open package webpage

        raise ValueError(f"'{args[0]}' is an invalid command")

    except:
        e_type,e_value,e_trace = sys.exc_info()
        if e_type in exceptions if exceptions else []:
            raise
        stderr(f"{e_type.__name__} {e_value}")
        return E_EXCEPTION

if __name__ == "__main__":

    main(['index'])