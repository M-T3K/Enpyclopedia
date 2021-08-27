"""
A python interface to retrieve information from online encyclopedias. 
The following Encyclopedias are covered:
- Wikipedia
- Omniglot
The following Encyclopedias may be covered in the future:
- Wolfram
"""
import logging
import requests
from bs4 import BeautifulSoup
import re
# @debug
import json # For requests and pretty printing
import urllib.parse

LOGGER = logging.getLogger(__name__)
WIKI_API_URL = "https://en.wikipedia.org/w/api.php"

class WikipediaSection:

    def __init__(self, sect: dict) -> None:
        self.toclevel = sect["toclevel"]
        self.level = sect["level"]
        self.line = sect["line"]
        self.number = sect["number"]
        self.index = sect["index"]
        self.fromtitle = sect["fromtitle"]
        self.byteoffset = sect["byteoffset"]
        self.anchor = sect["anchor"]
    # END

    def get_text(self, type="text") -> str:
        """
        Retrieves the full text of the section
        @arg type: There are two possible types of queries. The default option is "text" and retrieves the html code, while the "wikitext" option retrieves it in a wiki format.
        @return String
        """
        if type != "text" and type != "wikitext":
            return ""
        # https://www.mediawiki.org/w/api.php?action=parse&page=API:Parsing_wikitext&section=1&prop=text

        query_params = {
                "action": "parse",
                "format": "json",
                "page": f"{self.fromtitle}",
                "prop": f"{type}",
                "section": f"{self.index}"
            }

        req = requests.Session().get(url=WIKI_API_URL, params=query_params)
        return req.json()["parse"][f"{type}"]["*"]

# END
class WikipediaPage:

    # https://www.mediawiki.org/wiki/API:Info
    def __init__(self, page: dict):
        # Bare minimum for a Wikipedia Page
        self.pageid = page["pageid"]
        self.ns = page["ns"]
        self.title = page["title"]

        keys = page.keys()
        # @info we don't really have to check the rest in our case
        if "contentmodel" in keys: 
            self.contentmodel = page["contentmodel"]
            self.pagelanguage = page["pagelanguage"]
            self.pagelanguagehtmlcode = page["pagelanguagehtmlcode"]
            self.pagelanguagedir = page["pagelanguagedir"]
            self.touched = page["touched"]
            self.lastrevid = page["lastrevid"]
            self.length = page["length"]
            self.talkid = page["talkid"]
            self.fullurl = page["fullurl"]
            self.editurl = page["editurl"]
            self.canonicalurl = page["canonicalurl"]
        if "redirects" in keys:
            self.redirects = [ WikipediaPage(pg) for pg in page["redirects"]]
        
        # @optimization Requests are much slower than a memory access so we keep track of the 
        # requested html or sections. These may need to be accessed multiple times...
        self.html = ""
        self.sections = []
    # END

    def is_redirect(self) -> str:
        """
        Checks wether or not the WikipediaObject is actually a redirection to another page.
        The returning string contains the title of the page it redirects to, or an empty string if it isn't a redirection
        @return String
        """

        if self.html == "":
            page = requests.get(self.fullurl)
            self.html = BeautifulSoup(page.content, 'html.parser')

        is_redirect = self.html.find('span', {"class": "mw-redirectedfrom"})
        if is_redirect:
            return self.html.find('h1', {"id": "firstHeading", "class": "firstHeading"}).text
        return ""
    # END

    def get_summary(self) -> str:
        """
        Returns the first section of text of a specific wikipedia page, which acts like a summary of the page.
        @return String
        """
        summary = ""
        query_params = {
                "action": "query",
                "format": "json",
                "titles": f"{self.title}",
                "prop": "extracts",
                "exintro": None,
                "explaintext": None
            }

        params_str = '&'.join([k if v is None else f"{k}={v}" for k, v in query_params.items()])
        req = requests.Session().get(url=WIKI_API_URL, params=params_str)
        
        resp = req.json()
        for k, pg in resp["query"]["pages"].items():
            if k != "-1":
                summary = pg["extract"].strip()
            # END
        # END
        return summary
    # END

    def get_other_languages(self) -> list:
        """
        Returns the links for the current page in all other available languages.
        @return List of strings
        """
        query_params = {
                "action": "query",
                "format": "json",
                "titles": f"{self.title}",
                "prop": "langlinks"
            }

        req = requests.Session().get(url=WIKI_API_URL, params=query_params)
        
        resp = req.json()
        final_links = []
        for k, pg in resp["query"]["pages"].items():
            if k != "-1":
                links = pg["langlinks"]
                for l in links:
                    code = l["lang"]
                    new_title = urllib.parse.quote(l["*"])
                    final_links.append(f"https://{code}.wikipedia.org/wiki/{new_title}")
            # END
        # END
        if len(final_links) == 0:
            return None
        return final_links
    # END

    def get_full_text(self, type="text") -> str:
        """
        Retrieves the full text of the webpage.
        @arg type: There are two possible types of queries. The default option is "text" and retrieves the html code, while the "wikitext" option retrieves it in a wiki format.
        @return String
        """
        if type != "text" and type != "wikitext":
            return ""
        query_params = {
                "action": "parse",
                "format": "json",
                "page": f"{self.title}",
                "prop": f"{type}"
            }

        req = requests.Session().get(url=WIKI_API_URL, params=query_params)
        return req.json()["parse"][f"{type}"]["*"]
    # END

    def get_sections(self) -> list:
        # https://www.mediawiki.org/w/api.php?action=parse&page=API:Parsing_wikitext&prop=sections
        # print(self.sections)
        if self.sections:
            return self.sections
        
        query_params = {
                "action": "parse",
                "format": "json",
                "page": f"{self.title}",
                "prop": "sections"
            }

        req = requests.Session().get(url=WIKI_API_URL, params=query_params)
        # print(req.url)
        sects = req.json()["parse"]["sections"]
        # print(json.dumps(sects, indent=4))
        self.sections = []
        for s in sects:
            self.sections.append(WikipediaSection(s))
        return self.sections
# END


class Enpyclopedia:

    def __init__(self, encyclopedia="ALL"):
        """
        Constructor that takes a single parameter: what kind of encyclopedia we are going to use.
        By Default, the member encyclopedia is 'ALL', meaning that it will try to find the 
        information in all supported encyclopedias.
        """
        self.encyclopedia = encyclopedia.upper()
        self.pages = [] # List of all querried pages/sites for later access
        self.last_page_index = -1 # Index of the last page in the pages list, starts at -1 (no last page)
        # END
    # END INIT

    def find(self, to_find: str) -> None:
        """
        Method that finds specific information on the appropriate online encyclopedia.
        It can be either a string containing the information to search for or link.
        If the page exists, it creates a WikipediaPage object and stores 
        all necessary information. The object is then added to the self.pages list.
        The last_page_index is then incremented.
        If the page doesn't exist, it returns False
        If at least one page is found, it returns True.

        """

        match_found = False

        if self.encyclopedia == "WIKIPEDIA" or self.encyclopedia == "ALL":
            S = requests.Session()
            title = to_find

            # @info Basic Link checking, the more robust option would involve regex but
            # for our purposes I think that would be overkill.
            if "https://" in to_find or "http://" in to_find:
                # We want the title of the page if we know the link.
                # This is essentially the last part of the url string
                title = to_find.split('/')
                title = title[len(title) - 1]
            # END

            query_params = {
                "action": "query",
                "format": "json",
                "titles": f"{title}",
                "prop": "info|redirects",
                "inprop": "url|talkid"
            }
            resp = S.get(url=WIKI_API_URL, params=query_params).json()
            for k, pg in resp["query"]["pages"].items():
                if k != "-1":
                    page = WikipediaPage(page=pg)
                    self.pages.append(page)
                    self.last_page_index += 1
                    match_found = True
                # END
            # END
            
        if self.encyclopedia == "OMNIGLOT" or self.encyclopedia == "ALL":
            pass
        return match_found
    # END

# END CLASS