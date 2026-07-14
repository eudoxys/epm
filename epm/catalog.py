"""Eudoxys package catalog"""

import os
import sys
import re
import urllib.request
import requests
import tomllib

class CatalogError(Exception):
    pass

class Catalog:

    REPO = "https://github.com/eudoxys"
    """Repository owner"""

    DATA = "https://raw.githubusercontent.com/eudoxys"
    """Repository data access path"""

    LIST = None # flag for scanning repos instead of explicit list
    """Default list of packages (use `None` to scan repositories)"""
    # LIST = [   
    #     "eia",
    #     "epm",
    #     "eudoxys",
    #     "geohash",
    #     "gld_pypower",
    #     "load_model",
    #     "loaddata",
    #     "mailer",
    #     "mguid",
    #     "nsrdb",
    #     "project",
    #     "pypower_api",
    #     "qdox",
    #     "retail",
    #     "states",
    # ]

    CACHEFILE = None # os.path.join(os.environ['HOME'],".epm_list")
    """Catalog cache file (`None` to disable cache)"""

    ACCESS_TOKEN = os.path.join(os.environ['HOME'],".github","access-token")
    """Access token file path"""

    def __init__(self,pattern:list[str]|str=None):

        if self.LIST is None:
            self.scanrepos()

        if isinstance(pattern,list):
            self.index = []
            for item in pattern:
                self.index.extend([x for x in self.LIST if re.match(item,x)])
        else:
            self.index = [x for x in self.LIST if not pattern or re.match(pattern,x)]

    classmethod
    def scanrepos(cls,refresh=False):
        if not cls.CACHEFILE is None and os.path.exists(cls.CACHEFILE):
            with open(cls.CACHEFILE,"r") as fh:
                cls.LIST = json.load(fh)
        else:
            cls.LIST = []
            page = 1
            per_page = 100  # Maximum allowed by GitHub per request
            
            # Set up headers with optional authentication for private repos
            headers = {"Accept": "application/vnd.github+json"}
            if os.path.exists(cls.ACCESS_TOKEN):
                with open(cls.ACCESS_TOKEN,"r") as fh:
                    token = fh.read().strip()
                    headers["Authorization"] = f"Bearer {token}"
            
            while True:
                url = f"https://api.github.com/orgs/{'eudoxys'}/repos?page={page}&per_page={per_page}"
                response = requests.get(url, headers=headers)
                
                if response.status_code != 200:
                    print(f"Error fetching data: {response.status_code} - {response.text}")
                    break
                    
                data = response.json()
                
                # Break the loop if no more repositories are returned
                if not data:
                    break

                cls.LIST.extend([x["name"] for x in data])
                    
                page += 1

            if not cls.CACHEFILE is None:
                with open(cls.CACHEFILE,"w") as fh:
                    json.dump(cls.LIST,fh,indent=4)
                
    def repository(self,product):
        assert product in self.index, f"{product} is not in catalog index"
        return os.path.join(self.REPO,product)

    def metadata(self,product):
        assert product in self.index, f"{product} is not in catalog index"
        url = os.path.join(self.DATA,product,"refs","heads","main","pyproject.toml")
        try:
            with urllib.request.urlopen(url) as query:
                return tomllib.loads(query.read().decode('utf-8'))
        except urllib.request.HTTPError as err:
            if url.endswith("pyproject.toml"):
                return None
        except:
            e_type,e_value,e_trace = sys.exc_info()
            raise CatalogError(f"({e_type.__name__}) {e_value} from {url=}")

    def print(self,print=print,all=False):
        if self.index:
            result = {}
            header = ["product","version","type","description"]
            underline = {x:len(x) for x in header}
            for product in self.index:
                info = self.metadata(product)
                if info and isinstance(info,dict) and "project" in info:
                    if all or ( "version" in info["project"] and info["project"]["version"] > "0.0.0"):
                        # import json
                        try:
                            description = info["project"]["description"].split("\n")[0].strip("# ")
                        except KeyError:
                            description = ""
                        try:
                            version = info["project"]["version"]
                        except KeyError:
                            version = ""
                        type = "M"
                        if "tools" in info and "setuptools" in info["tools"] and "packages" in info["tools"]["setuptools"]:
                            type += "P"
                        else:
                            type += "-"
                        if "project" in info and "scripts" in info["project"] and len(info["project"]["scripts"]) > 0:
                            type += "C"
                        else:
                            type += "-"
                        if "keywords" in info["project"] and "eudoxys" in info["project"]["keywords"]:
                            type += "E"
                        else:
                            type += "-"
                        result[product] = {x:eval(x) for x in header}
                        underline = {x:max(underline[x],len(eval(x))) for x in header}
            print(" ".join([x.title()+" "*(underline[x]-len(x)) for x in header]))
            print(" ".join(['-'*underline[x] for x in header]))
            for product,info in result.items():
                print(" ".join([y+" "*(underline[x]-len(y)) for x,y in info.items()]))


if __name__ == "__main__":

    import json

    catalog = Catalog()
    catalog.print()
    # catalog.print(all=True)
