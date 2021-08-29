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
from tqdm import tqdm
from wget import download
import os
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

# @info I considered adding a new member called "Type" that reflects the type of the WikipediaPage:
# For example, "Category", "Redirect", "Normal"
# But I've reached the conclusion that it would be terrible: as of rn, the only way a WikipediaPage 
# can be one of those things is if being accessed through another WikipediaPage's arguments, which
# implies that you must know what you are accessing. It is important to know what type of data you
# are accessing, even more so in dynamic languages like Python, so doing this would be a bad idea.
class WikipediaPage:

    # https://www.mediawiki.org/wiki/API:Info
    def __init__(self, page: dict):
        
        self.args = page
        keys = page.keys()

        # Special members
        # @optimization Requests are much slower than a memory access so we keep track of the 
        # requested html or sections. These may need to be accessed multiple times...
        self.html = ""
        self.sections = []
        self.categories = [] # Categories are a type of page

        if "redirects" in keys:
            self.redirects = [ WikipediaPage(pg) for pg in self.args["redirects"]]

    def is_redirect(self) -> str:
        """
        Checks wether or not the WikipediaObject is actually a redirection to another page.
        The returning string contains the title of the page it redirects to, or an empty string if it isn't a redirection
        @return String
        """

        if self.html == "":
            req = requests.get(self.args["fullurl"])
            LOGGER.info("Request URL: %s", req.url)
            self.html = BeautifulSoup(req.content, 'html.parser')

        is_redirect = self.html.find('span', {"class": "mw-redirectedfrom"})
        if is_redirect:
            return self.html.find('h1', {"id": "firstHeading", "class": "firstHeading"}).text
        return ""

    def get_summary(self) -> str:
        """
        Returns the first section of text of a specific wikipedia page, which acts like a summary of the page.
        @return String
        """
        summary = ""
        title = self.args["title"]
        query_params = {
                "action": "query",
                "format": "json",
                "titles": f"{title}",
                "prop": "extracts",
                "exintro": None,
                "explaintext": None
            }

        params_str = '&'.join([k if v is None else f"{k}={v}" for k, v in query_params.items()])
        req = requests.Session().get(url=WIKI_API_URL, params=params_str)
        LOGGER.info("Request URL: %s", req.url)
        for k, pg in req.json()["query"]["pages"].items():
            if k != "-1":
                summary = pg["extract"].strip()
        return summary

    def get_other_languages(self) -> list:
        """
        Returns the links for the current page in all other available languages.
        @return List of strings
        """
        title = self.args["title"]
        query_params = {
                "action": "query",
                "format": "json",
                "titles": f"{title}",
                "prop": "langlinks"
            }

        req = requests.Session().get(url=WIKI_API_URL, params=query_params)
        LOGGER.info("Request URL: %s", req.url)
        final_links = []
        for k, pg in req.json()["query"]["pages"].items():
            if k != "-1":
                links = pg["langlinks"]
                for l in links:
                    code = l["lang"]
                    new_title = urllib.parse.quote(l["*"])
                    final_links.append(f"https://{code}.wikipedia.org/wiki/{new_title}")
        return final_links

    def get_full_text(self, type="text") -> str:
        """
        Retrieves the full text of the webpage.
        @arg type: There are two possible types of queries. The default option is "text" and retrieves the html code, while the "wikitext" option retrieves it in a wiki format.
        @return String
        """
        if type != "text" and type != "wikitext":
            return ""
        title = self.args["title"]
        query_params = {
                "action": "parse",
                "format": "json",
                "page": f"{title}",
                "prop": f"{type}"
            }

        req = requests.Session().get(url=WIKI_API_URL, params=query_params)
        LOGGER.info("Request URL: %s", req.url)
        return req.json()["parse"][f"{type}"]["*"]

    def get_sections(self) -> list:
        """
        Retrieves all the sections of the current page. If the sections were already previously found, it returns the previous ones.
        @return a list of WikipediaSection containing all the sections. 
        """
        # https://www.mediawiki.org/w/api.php?action=parse&page=API:Parsing_wikitext&prop=sections
        if self.sections:
            LOGGER.warning("This WikipediaPage has already retrieved all of its sections at a previous time. Returning previously found sections to avoid unnecessary requests. ")
            return self.sections
        
        title = self.args["title"]
        query_params = {
                "action": "parse",
                "format": "json",
                "page": f"{title}",
                "prop": "sections"
            }

        req = requests.Session().get(url=WIKI_API_URL, params=query_params)
        LOGGER.info("Request URL: %s", req.url)
        sects = req.json()["parse"]["sections"]
        self.sections = []
        for s in sects:
            self.sections.append(WikipediaSection(s))
        return self.sections

    def get_categories(self) -> list:
        """
        Retrieves all the categories of the current page. If the categories were already previously found, it returns the previous ones.
        @return a list of WikipediaPage containing all the sections. 
        """
        if self.categories:
            LOGGER.warning("This WikipediaPage has already retrieved all of its categories at a previous time. Returning previously found categories to avoid unnecessary requests")
            return self.categories
        
        title = self.args["title"]
        query_params = {
                "action": "query",
                "format": "json",
                "titles": f"{title}",
                "prop": "categories"
            }

        req = requests.Session().get(url=WIKI_API_URL, params=query_params)
        LOGGER.info("Request URL: %s", req.url)
        self.categories = []
        for k, p in req.json()["query"]["pages"].items():
            if k != "-1":
                for s in p["categories"]:
                    self.categories.append(WikipediaPage(s))
        return self.categories

    def get_category_members(self, cmlimit = 20, cmprop = "", cmsort = "", cmdir = "", cmtype="", cmstarthexsortkey="", cmendhexsortkey="", cmstartsortkeyprefix="", cmendsortkeyprefix="", cmnamespace="") -> list:
        """
        It retrieves a certain amount (limited by cmlimit) of pages that belong to a specific category.
        This WikipediaPage object must be a Category for the method to work. 
        Full list of arguments can be found in the following link:
        https://www.mediawiki.org/wiki/API:Categorymembers
        @return [] if the current WikipediaPage object is not a Category, or a list of WikipediaPage objects of cmlimit length.
        """
        
        # https://www.mediawiki.org/wiki/API:Categorymembers
        # Check if this is a category (by finding the Category prefix)
        if self.args["title"].split(":")[0] != "Category":
            LOGGER.error("The current page (%s) is not a category.", self.args["title"])
            return [] # Not a category
        title = self.args["title"]
        query_params = {
                "action": "query",
                "format": "json",
                "list": "categorymembers",
                "cmtitle": f"{title}", # May have to do urllib quote()
                "cmlimit": f"{cmlimit}"
            }

        if cmprop != "":
            query_params["cmprop"] = cmprop
        if cmsort != "":
            query_params["cmsort"] = cmsort
            if cmsort == "sortkey":
                if cmstarthexsortkey != "":
                    query_params["cmstarthexsortkey"] = cmstarthexsortkey
                if cmstartsortkeyprefix != "":
                    query_params["cmstartsortkeyprefix"] = cmstartsortkeyprefix
                if cmendhexsortkey != "":
                    query_params["cmendhexsortkey"] = cmendhexsortkey
                if cmendsortkeyprefix != "":
                    query_params["cmendsortkeyprefix"] = cmendsortkeyprefix
        if cmdir != "":
            query_params["cmdir"] = cmdir
        if cmtype != "":
            query_params["cmtype"] = cmtype

        req = requests.Session().get(url=WIKI_API_URL, params=query_params)
        LOGGER.info("Request URL: %s", req.url)
        categorymembers = [ WikipediaPage(p) for p in req.json()["query"]["categorymembers"] ]
        return categorymembers

    def get_all_pages(self, aplimit=10, apdir="", apcontinue="", apto="", apprefix="", apnamespace="", apfilterredir="", apminsize="", apmaxsize="", apprtype="", apprlevel="", apprfiltercascade="", apfilterlanglinks="", apprexpiry="") -> list:
        """
        It retrieves a certain amount (limited by aplimit) of pages that can be found in the current page.
        Full list of arguments can be found in the following link:
        https://www.mediawiki.org/wiki/API:Allpages
        @return a list of WikipediaPage objects of cmlimit length.
        """
        title = self.args["title"]
        query_params = {
                "action": "query",
                "format": "json",
                "list": "allpages",
                "apfrom": f"{title}",
                "aplimit": f"{aplimit}"
            }
        
        if apdir != "":
            query_params["apdir"] = apdir
        if apcontinue != "":
            query_params["apcontinue"] = apcontinue
        if apto != "":
            query_params["apto"] = apto
        if apprefix != "":
            query_params["apprefix"] = apprefix
        if apnamespace != "":
            query_params["apnamespace"] = apdir
        if apfilterredir != "":
            query_params["apfilterredir"] = apfilterredir
        if apminsize != "":
            query_params["apminsize"] = apminsize
        if apmaxsize != "":
            query_params["apmaxsize"] = apmaxsize
        if apprtype != "":
            query_params["apprtype"] = apprtype
        if apprlevel != "":
            query_params["apprlevel"] = apprlevel
        if apprfiltercascade != "":
            query_params["apprfiltercascade"] = apprfiltercascade
        if apfilterlanglinks != "":
            query_params["apfilterlanglinks"] = apfilterlanglinks
        if apprexpiry != "":
            query_params["apprexpiry"] = apprexpiry

        req = requests.Session().get(url=WIKI_API_URL, params=query_params)
        LOGGER.info("Request URL: %s", req.url)
        allpages = [ WikipediaPage(p) for p in req.json()["query"]["allpages"] ]
        return allpages
        
    def get_all_imgs(self, directory="imgs\\") -> tuple(int, int):
        """
        Downloads using wget's package all images found in a webpage to the specified directory.
        @returns integer tuple that contains the amount of images downloaded and the total amount of images encountered. 
        Note that behaviour is non-blocking, meaning that encountering an error will not stop the method from attempting to download the rest of images found.
        """
        
        imgs_downloaded = 0
        if not os.path.isdir(directory):
            os.makedirs(directory)
        if self.html == "":
            req = requests.get(self.args["fullurl"])
            LOGGER.info("Request URL: %s", req.url)
            self.html = BeautifulSoup(req.content, 'html.parser')
        imgs = self.html.find_all('img')
        for img in tqdm(imgs):
            img_url = img.attrs.get("src")
            if img_url:
                img_url = urllib.parse.urljoin(self.args["fullurl"], img_url)
                img_url = img_url.split('?')[0] # Remove Query Params
                LOGGER.info("Downloading image from %s into %s", img_url, directory)
                try:
                    download(img_url, directory) # Download using wget
                    imgs_downloaded += 1
                except:
                    LOGGER.warning("Image with URL = < %s > could not be downloaded.", img_url)
                    continue

        # Cleanup of .tmp files
        files_found = [f for f in os.listdir() if f.endswith(".tmp")]
        for f in files_found:
            os.remove(f)
        return (imgs_downloaded, len(imgs))



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

    def find(self, to_find: str) -> bool:
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

            query_params = {
                "action": "query",
                "format": "json",
                "titles": f"{title}",
                "prop": "info|redirects",
                "inprop": "url|talkid"
            }
            req = S.get(url=WIKI_API_URL, params=query_params)
            LOGGER.info("Request URL: %s", req.url)

            for k, pg in req.json()["query"]["pages"].items():
                if k != "-1":
                    page = WikipediaPage(page=pg)
                    self.pages.append(page)
                    self.last_page_index += 1
                    match_found = True
            
        if self.encyclopedia == "OMNIGLOT" or self.encyclopedia == "ALL":
            pass
        return match_found
