"""Eudoxys package catalog"""

import os
import re
import urllib.request
import tomllib

class Catalog:

    REPO = "https://github.com/eudoxys"
    DATA = "https://raw.githubusercontent.com/eudoxys"
    LIST = [   
        "epm",
    ]

    def __init__(self,pattern:str=None):
        self.index = [x for x in self.LIST if not pattern or re.match(pattern,x)]

    def repository(self,package):
        assert package in self.index, f"{package} is not in catalog index"
        return os.path.join(self.REPO,package)

    def metadata(self,package):
        assert package in self.index, f"{package} is not in catalog index"
        url = os.path.join(self.DATA,package,"refs","heads","main","pyproject.toml")
        with urllib.request.urlopen(url) as query:
            return tomllib.loads(query.read().decode('utf-8'))

if __name__ == "__main__":

    import json

    catalog = Catalog()
    if catalog.index:
        result = {}
        header = ["package","version","description"]
        underline = {x:len(x) for x in header}
        for package in catalog.index:
            info = Catalog().metadata(package)
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
