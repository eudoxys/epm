"""Eudoxys package manager

Syntax: epm [OPTIONS ...] COMMAND [ARGUMENTS ...]

Options:

    -h|--help: get this help

Commands:

    help: get this help

    list: get list of installed packages
"""

import os
import sys

def main(
    args=sys.argv[1:],
    stdout=lambda x: print(x,file=sys.stdout),
    stderr=lambda x: print(x if x.startswith("Syntax: ") else f"ERROR [epm]: {x}",file=sys.stderr),
    exceptions=None
    ):

    try:
        E_OK = 0
        E_SYNTAX = 1
        E_EXCEPTION = 9

        if len(args) == 0:

            stderr("\n".join([x for x in __doc__.split("\n") if x.startswith("Syntax: ")]))
            return E_SYNTAX

        if args[0] in ["-h","--help","help"]:

            stdout(__doc__)
            return E_OK

        if args[0] == "list":

            stdout("No packages installed")
            return E_OK

        raise ValueError(f"'{args[0]}' is an invalid command")

    except:
        e_type,e_value,e_trace = sys.exc_info()
        if e_type in exceptions if exceptions else []:
            raise
        stderr(f"{e_type.__name__} {e_value}")
        return E_EXCEPTION
