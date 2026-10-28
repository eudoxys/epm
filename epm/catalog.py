"""Eudoxys package catalog

Lists the repositories of the `eudoxys` GitHub organization and reads each
one's `pyproject.toml` from its `main` branch.

Examples
--------

    from epm import Catalog
    Catalog("epm").print()

outputs

    Product Version Type Description
    ------- ------- ---- -----------------------
    epm     26.10.0 MPCE Eudoxys Package Manager

Type codes
----------

The `Type` column has four flags, one per position, with `-` in a position
whose condition does not hold:

| Position | Code | Meaning                                  | Condition in `pyproject.toml`            |
| :------: | :--: | ---------------------------------------- | ---------------------------------------- |
| 1        | `M`  | Eudoxys managed package                  | the file exists and has `[project]`      |
| 2        | `P`  | Setuptools package list                  | `[tool.setuptools] packages` is set      |
| 3        | `C`  | Command line interface                   | `[project.scripts]` defines a command    |
| 4        | `E`  | Eudoxys support enabled (official release) | `[project] keywords` includes `eudoxys` |

Packages without a `pyproject.toml` are not listed, so position 1 is always
`M`.

Caveats
-------

  - Each `Catalog()` queries the GitHub API unless `Catalog.LIST` is set or
    `Catalog.CACHEFILE` holds a cached list. Unauthenticated requests are
    rate-limited by GitHub (60 per hour); put a token in
    `Catalog.ACCESS_TOKEN` to raise the limit and to see private repositories.
  - Version comparison against `0.0.0` is a string comparison.

References
----------

  - https://docs.github.com/en/rest/repos/repos#list-organization-repositories
"""

import os
import sys
import re
import json
import logging
import urllib.request
import tomllib

import requests

_logger = logging.getLogger(__file__)

class CatalogError(Exception):
    """Catalog access error"""

class Catalog:
    """Index of the packages in the eudoxys GitHub organization"""

    REPO = "https://github.com/eudoxys"
    """Repository owner"""

    DATA = "https://raw.githubusercontent.com/eudoxys"
    """Repository data access path"""

    LIST = None # `None` to scan repos instead of explicit list
    """Default list of packages (use `None` to scan repositories)"""

    CACHEFILE = None # os.path.join(os.environ['HOME'],".epm_list")
    """Catalog cache file (`None` to disable cache)"""

    ACCESS_TOKEN = os.path.join(os.path.expanduser("~"),".github","access-token")
    """Access token file path"""

    def __init__(self,pattern:list[str]|str|None=None):
        """Create a catalog index

        Arguments
        ---------

        - `pattern`: regular expression (or list of them) matched against
          package names (`None` for all packages)

        Exceptions
        ----------

        - `CatalogError`: the GitHub organization could not be scanned
        """

        if self.LIST is None:
            self.scanrepos()

        if isinstance(pattern,list):
            self.index = []
            for item in pattern:
                self.index.extend([x for x in self.LIST if re.match(item,x)])
        else:
            self.index = [x for x in self.LIST if not pattern or re.match(pattern,x)]

    @classmethod
    def scanrepos(cls,
        refresh:bool=False,
        ) -> None:
        """Scan org repos for packages

        Arguments
        ---------

        - `refresh`: force refresh of cache if `epm.catalog.CACHEFILE` is not `None`

        Description
        -----------

        This class method set `epm.catalog.LIST` by scanning the organization
        repositories.
        """
        if not cls.CACHEFILE is None and os.path.exists(cls.CACHEFILE) and not refresh:
            _logger.debug("reading catalog cache %s",cls.CACHEFILE)
            with open(cls.CACHEFILE,"r",encoding="utf-8") as fh:
                cls.LIST = json.load(fh)
        else:
            cls.LIST = []
            page = 1
            per_page = 100  # Maximum allowed by GitHub per request
            
            # Set up headers with optional authentication for private repos
            headers = {"Accept": "application/vnd.github+json"}
            if os.path.exists(cls.ACCESS_TOKEN):
                with open(cls.ACCESS_TOKEN,"r",encoding="utf-8") as fh:
                    token = fh.read().strip()
                    headers["Authorization"] = f"Bearer {token}"
            
            while True:
                url = f"https://api.github.com/orgs/{'eudoxys'}/repos?page={page}&per_page={per_page}"
                _logger.debug("scanning %s",url)
                response = requests.get(url, headers=headers, timeout=30)
                
                if response.status_code != 200:
                    raise CatalogError(f"unable to scan {url} ({response.status_code} - {response.text})")
                    
                data = response.json()
                
                # Break the loop if no more repositories are returned
                if not data:
                    break

                cls.LIST.extend([x["name"] for x in data])
                    
                page += 1

            if not cls.CACHEFILE is None:
                with open(cls.CACHEFILE,"w",encoding="utf-8") as fh:
                    json.dump(cls.LIST,fh,indent=4)
                
    def repository(self,product:str) -> str:
        """Get repository from product name

        Arguments
        ---------

        - `product`: package name
        """
        assert product in self.index, f"{product} is not in catalog index"
        return os.path.join(self.REPO,product)

    def metadata(self,product:str) -> dict|None:
        """Get repository metadata from product name

        Arguments
        ---------

        - `product`: package name

        Returns
        -------

        - `dict`: the parsed `pyproject.toml`, or `None` if the repository
          has none
        """
        assert product in self.index, f"{product} is not in catalog index"
        url = os.path.join(self.DATA,product,"refs","heads","main","pyproject.toml")
        try:
            with urllib.request.urlopen(url) as query:
                return tomllib.loads(query.read().decode('utf-8'))
        except urllib.request.HTTPError:
            _logger.debug("%s has no pyproject.toml",product)
            return None
        except Exception as err: # pylint: disable=broad-exception-caught
            e_type,e_value,_ = sys.exc_info()
            raise CatalogError(f"({e_type.__name__}) {e_value} from {url=}") from err

    def print(self,
        print:callable=print, # pylint: disable=redefined-builtin,used-before-assignment
        all:bool=False, # pylint: disable=redefined-builtin
        ) -> None:
        """Print catalog

        Arguments
        ---------

        - `print`: print call (defaults to `print`)

        - `all`: include unreleased packages (version `0.0.0` or missing)

        Description
        -----------

        The following columns are output.

        - **Product**: The package name used by `pip` after installation.
        
        - **Version**: The latest package release version number.

        - **Type**: The package type information, i.e.,
          - `M`: Eudoxys managed package using `epm`
          - `P`: Setuptools supported (deprecated setup)
          - `C`: Command script supported
          - `E`: Eudoxys support enabled (official release)

        - **Description**: The description from the `pyproject.toml` file.
        
        """
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
                        if "tool" in info and "setuptools" in info["tool"] and "packages" in info["tool"]["setuptools"]:
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
                        row = {"product":product,"version":version,"type":type,"description":description}
                        result[product] = row
                        underline = {x:max(underline[x],len(row[x])) for x in header}
            print(" ".join([x.title()+" "*(underline[x]-len(x)) for x in header]))
            print(" ".join(['-'*underline[x] for x in header]))
            for product,info in result.items():
                print(" ".join([y+" "*(underline[x]-len(y)) for x,y in info.items()]))


if __name__ == "__main__":

    catalog = Catalog()
    catalog.print()
    # catalog.print(all=True)
