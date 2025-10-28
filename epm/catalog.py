"""Eudoxys package catalog"""

import os
import sys
import re
import urllib.request
import tomllib

class CatalogError(Exception):
    pass

class Catalog:

    REPO = "https://github.com/eudoxys"
    DATA = "https://raw.githubusercontent.com/eudoxys"
    LIST = [   
        "eia",
        "epm",
        "eudoxys",
        "geocode",
        "gld_pypower",
        "load_model",
        "loaddata",
        "mailer",
        "mguid",
        "nsrdb",
        "project",
        "pypower_api",
        "qdox",
        "retail",
        "states",
    ]

    def __init__(self,pattern:list[str]|str=None):
        if isinstance(pattern,list):
            self.index = []
            for item in pattern:
                self.index.extend([x for x in self.LIST if re.match(item,x)])
        else:
            self.index = [x for x in self.LIST if not pattern or re.match(pattern,x)]

    def repository(self,package):
        assert package in self.index, f"{package} is not in catalog index"
        return os.path.join(self.REPO,package)

    def metadata(self,package):
        assert package in self.index, f"{package} is not in catalog index"
        url = os.path.join(self.DATA,package,"refs","heads","main","pyproject.toml")
        try:
            with urllib.request.urlopen(url) as query:
                return tomllib.loads(query.read().decode('utf-8'))
        except urllib.request.HTTPError as err:
            if url.endswith("pyproject.toml"):
                return None
        except:
            e_type,e_value,e_trace = sys.exc_info()
            raise CatalogError(f"({e_type.__name__}) {e_value} from {url=}")

    def print(self,print=print):
        if self.index:
            result = {}
            header = ["package","version","description"]
            underline = {x:len(x) for x in header}
            for package in self.index:
                info = Catalog().metadata(package)
                if info:
                    import json
                    try:
                        description = info["project"]["description"].split("\n")[0].strip("# ")
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


if __name__ == "__main__":

    import json

    catalog = Catalog()
    catalog.print()
    # if catalog.index:
    #     result = {}
    #     header = ["package","version","description"]
    #     underline = {x:len(x) for x in header}
    #     for package in catalog.index:
    #         info = Catalog().metadata(package)
    #         try:
    #             description = info["project"]["description"]
    #         except KeyError:
    #             description = ""
    #         try:
    #             version = info["project"]["version"]
    #         except KeyError:
    #             version = ""
    #         result[package] = {x:eval(x) for x in header}
    #         underline = {x:max(underline[x],len(eval(x))) for x in header}
    #     print(" ".join([x.title()+" "*(underline[x]-len(x)) for x in header]))
    #     print(" ".join(['-'*underline[x] for x in header]))
    #     for package,info in result.items():
    #         print(" ".join([y+" "*(underline[x]-len(y)) for x,y in info.items()]))
