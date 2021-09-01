"""
A python interface to retrieve information from online encyclopedias. 
The following Encyclopedias are covered:
- Wikipedia
The following Encyclopedias may be covered in the future:
- Omniglot
- Wolfram
"""
import logging
import requests
from bs4 import BeautifulSoup
from wget import download
from tqdm import tqdm # This is a progress bar for when images are being downloaded
from dataclasses import dataclass
import os
import urllib.parse
from typing import Tuple, Union

LOGGER = logging.getLogger(__name__)
WIKI_API_URL = "https://en.wikipedia.org/w/api.php"
# @info General API Information
# https://www.mediawiki.org/wiki/API:Info

# @info Classes
@dataclass
class WikipediaEntry:
    """
    The most basic data that can be retrieved using a GET request for any type of WikipediaEntry
    This data is common to all Entries, no matter the type.
    """
    ns: int
    title: str

@dataclass
class WikipediaEntryID(WikipediaEntry):
    """
    This type of Entry includes a page id for the page it refers to.
    """
    pageid: int

@dataclass
class WikipediaEntryPage(WikipediaEntryID):
    """
    This class contains all the information that can be retrieved of a page.
    """
    contentmodel: str
    pagelanguage: str
    pagelanguagehtmlcode: str
    pagelanguagedir: str
    touched: str
    lastrevid: int
    length: int
    talkid: int
    fullurl: str
    editurl: str
    canonicalurl: str
    # @optimization
    # Cached Dynamic Fields (Used to avoid unnecessary requests - requests are expensive!)
    redirects: list = None
    sections: list = None
    categories: list = None
    html: BeautifulSoup = None

@dataclass
class WikipediaSection:
    toclevel: str
    level: str    
    line: str
    number: str
    index: str
    fromtitle: str
    byteoffset: str
    anchor: str

# Functions

def get_html(url: str):
    req = requests.get(url)
    LOGGER.info("Request URL: %s", req.url)
    return BeautifulSoup(req.content, 'html.parser')

def is_redirecting(wiki_page: WikipediaEntryPage) -> str:
    """
    Checks wether or not the WikipediaEntryPage is redirecting to another page.
    A page that is redirecting to another one will not inherit certain fields on a request like Sections.
    @return String containing the title of the page it redirects to, or None if it isn't a redirection
    """

    if not wiki_page.html:
        wiki_page.html = get_html(wiki_page.fullurl)

    redirecting = wiki_page.html.find('span', {"class": "mw-redirectedfrom"})
    if redirecting:
        return wiki_page.html.find('h1', {"id": "firstHeading", "class": "firstHeading"}).text
    return None

def get_summary(wiki_page: WikipediaEntryPage) -> str:
    """
    Retrieves the first section of text of a specific wikipedia page, which acts like a summary of the page.
    @return String containing the summary of the page (text from the first section).
    """
    summary = ""
    query_params = {
            "action": "query",
            "format": "json",
            "titles": wiki_page.title,
            "prop": "extracts",
            "exintro": None,
            "explaintext": None
        }
    # @info Creating REST Query String without "None"
    params_str = '&'.join([k if v is None else f"{k}={v}" for k, v in query_params.items()])
    req = requests.Session().get(url=WIKI_API_URL, params=params_str)
    LOGGER.info("Request URL: %s", req.url)
    for k, pg in req.json()["query"]["pages"].items():
        if k != "-1":
            summary = pg["extract"].strip()
    return summary

def get_wiki_text(wiki_data: Union[WikipediaEntryPage, WikipediaSection], type="text") -> str:
    """
    Retrieves the full text of the WikipediaPage
    @arg type: There are two possible types of queries. The default option is "text" and retrieves the html code, while the "wikitext" option retrieves it in a wiki format.
    @return String
    """
    if not (isinstance(wiki_data, WikipediaEntryPage) or isinstance(wiki_data, WikipediaSection)):
        LOGGER.error("get_wiki_text() called with an argument that was neither a WikipediaEntryPage nor a WikipediaSection.")
        return None # If it's neither a page nor a section, abort
    if type != "text" and type != "wikitext":
        LOGGER.error("get_wiki_text() called with argument type = '%s' but can only be 'text' or 'wikitext'.", type)
        return None
    query_params = {
            "action": "parse",
            "format": "json",
            "prop": type
        }
    
    # https://www.mediawiki.org/w/api.php?action=parse&page=API:Parsing_wikitext&section=1&prop=text
    if isinstance(wiki_data, WikipediaSection):
        query_params["section"] = wiki_data.index
        query_params["page"] = wiki_data.fromtitle
    else:
        query_params["page"] = wiki_data.title

    req = requests.Session().get(url=WIKI_API_URL, params=query_params)
    LOGGER.info("Request URL: %s", req.url)
    return req.json()["parse"][type]["*"]

def get_other_languages(wiki_page: WikipediaEntryPage) -> list:
    """
    Returns the links for the current page in all other available languages.
    @return List of strings
    """
    query_params = {
            "action": "query",
            "format": "json",
            "titles": wiki_page.title,
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

def get_sections(wiki_page: WikipediaEntryPage) -> list:
    """
    Retrieves all the sections of the current page. If the sections were already previously found, it returns the previous ones.
    @return a list of WikipediaSection containing all the sections. 
    """
    # https://www.mediawiki.org/w/api.php?action=parse&page=API:Parsing_wikitext&prop=sections
    if wiki_page.sections:
        LOGGER.warning("This WikipediaEntryPage has already retrieved all of its sections at a previous time. Returning previously found sections to avoid unnecessary requests. ")
        return wiki_page.sections
    
    # @info This check provides useful information to the user that otherwise may take a while to figure out
    redirecting_check = is_redirecting(wiki_page)
    if redirecting_check:
        LOGGER.warning("This WikipediaEntryPage (%s) is redirecting to another page (%s). It's likely that sections do not appear.", wiki_page.title, redirecting_check)

    query_params = {
            "action": "parse",
            "format": "json",
            "page": wiki_page.title,
            "prop": "sections"
        }

    req = requests.Session().get(url=WIKI_API_URL, params=query_params)
    LOGGER.info("Request URL: %s", req.url)
    sects = req.json()["parse"]["sections"]
    wiki_page.sections = []
    
    for s in sects:
        wiki_page.sections.append(WikipediaSection(toclevel=s["toclevel"], level=s["level"], line=s["line"], number=s["number"], index=s["index"], fromtitle=s["fromtitle"], anchor=s["anchor"], byteoffset=s["byteoffset"]))
    
    # Error checking
    if not wiki_page.sections:
        LOGGER.warning("No sections found for page '%s'. Checking if page is redirecting...", wiki_page.title)
        redirecting_check = is_redirecting(wiki_page)
        if redirecting_check:
            LOGGER.warning("This WikipediaEntryPage '%s' is redirecting to another page (%s). The MediaWiki API does not return the sections for redirecting pages.", wiki_page.title, redirecting_check)
        else:
            LOGGER.error("No sections found and page '%s' was not redirecting to another one. You should manually check the request url '%s' to see what's wrong.", wiki_page.title, req.url)
            return None
    return wiki_page.sections

def get_categories(wiki_page: WikipediaEntryPage) -> list:
    """
    Retrieves all the categories of the current page. If the categories were already previously found, it returns the previous ones.
    @return a list of WikipediaEntryPage containing all the sections. 
    """
    if wiki_page.categories:
        LOGGER.warning("This WikipediaEntryPage has already retrieved all of its categories at a previous time. Returning previously found categories to avoid unnecessary requests")
        return wiki_page.categories
    
    query_params = {
            "action": "query",
            "format": "json",
            "titles": wiki_page.title,
            "prop": "categories"
        }

    req = requests.Session().get(url=WIKI_API_URL, params=query_params)
    LOGGER.info("Request URL: %s", req.url)
    wiki_page.categories = []
    for k, p in req.json()["query"]["pages"].items():
        if k != "-1":
            for s in p["categories"]:
                wiki_page.categories.append(WikipediaEntry(ns=int(s["ns"]), title=s["title"]))
    return wiki_page.categories

def get_category_members(wiki_category: WikipediaEntry, cmlimit = 20, cmprop = "", cmsort = "", cmdir = "", cmtype="", cmstarthexsortkey="", cmendhexsortkey="", cmstartsortkeyprefix="", cmendsortkeyprefix="", cmnamespace="") -> list:
    """
    It retrieves a certain amount (limited by cmlimit) of pages that belong to a specific category.
    This WikipediaEntryPage object must be a valid Category for the method to work. 
    Full list of arguments can be found in the following link:
    https://www.mediawiki.org/wiki/API:Categorymembers
    @return None if the current WikipediaEntryPage object is not a Category, or a list of WikipediaEntryPage objects of cmlimit length.
    """
    
    # https://www.mediawiki.org/wiki/API:Categorymembers
    # Check if this is a category (by finding the Category prefix)
    if wiki_category.title.split(":")[0] != "Category":
        LOGGER.error("The current page (%s) is not a category.", wiki_category.title)
        return None # Not a category
    query_params = {
            "action": "query",
            "format": "json",
            "list": "categorymembers",
            "cmtitle": wiki_category.title, # May have to do urllib quote()
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
    categorymembers = [ WikipediaEntryID(ns=int(p["ns"]), title=p["title"], pageid=int(p["pageid"])) for p in req.json()["query"]["categorymembers"] ]
    return categorymembers

def get_all_pages(wiki_page: WikipediaEntryPage, aplimit=10, apdir="", apcontinue="", apto="", apprefix="", apnamespace="", apfilterredir="", apminsize="", apmaxsize="", apprtype="", apprlevel="", apprfiltercascade="", apfilterlanglinks="", apprexpiry="") -> list:
    """
    It retrieves a certain amount (limited by aplimit) of pages that can be found in the current page.
    Full list of arguments can be found in the following link:
    https://www.mediawiki.org/wiki/API:Allpages
    @return a list of WikipediaEntryPage objects of cmlimit length.
    """
    query_params = {
            "action": "query",
            "format": "json",
            "list": "allpages",
            "apfrom": wiki_page.title,
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
    allpages = [  WikipediaEntryID(ns=int(p["ns"]), title=p["title"], pageid=int(p["pageid"])) for p in req.json()["query"]["allpages"] ]
    return allpages
    
def get_all_imgs(wiki_page: WikipediaEntryPage, base_directory="imgs\\") -> Tuple[int, int]:
    """
    Downloads using wget's package all images found in a webpage to the specified directory.
    @returns integer tuple that contains the amount of images downloaded and the total amount of images encountered. 
    Note that behaviour is non-blocking, meaning that encountering an error will not stop the method from attempting to download the rest of images found.
    """
    
    imgs_downloaded = 0

    directory = os.path.join(base_directory, wiki_page.title)

    if not os.path.isdir(directory):
        os.makedirs(directory)
    if not wiki_page.html:
        wiki_page.html = get_html(wiki_page.fullurl)
    imgs = wiki_page.html.find_all('img')
    for img in tqdm(imgs):
        img_url = img.attrs.get("src")
        if img_url:
            img_url = urllib.parse.urljoin(wiki_page.fullurl, img_url)
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
        If the page exists, it creates a WikipediaEntryPage object and stores 
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
                "titles": title,
                "prop": "info|redirects",
                "inprop": "url|talkid"
            }
            req = S.get(url=WIKI_API_URL, params=query_params)
            LOGGER.info("Request URL: %s", req.url)

            for k, pg in req.json()["query"]["pages"].items():
                if k != "-1":
                    page = WikipediaEntryPage(ns=pg["ns"], title=pg["title"], pageid=int(pg["pageid"]), contentmodel=pg["contentmodel"], pagelanguage=pg["pagelanguage"], pagelanguagehtmlcode=pg["pagelanguagehtmlcode"], pagelanguagedir=pg["pagelanguagedir"], touched=pg["touched"], lastrevid=int(pg["lastrevid"]), length=int(pg["length"]), talkid=int(pg["talkid"]), fullurl=pg["fullurl"], editurl=pg["editurl"], canonicalurl=pg["canonicalurl"])
                    if "redirects" in pg.keys():
                        page.redirects = [ WikipediaEntryID(ns=int(redir["ns"]), title=redir["title"], pageid=int(redir["pageid"])) for redir in pg["redirects"] ]
                    self.pages.append(page)
                    self.last_page_index += 1
                    match_found = True
            
        if self.encyclopedia == "OMNIGLOT" or self.encyclopedia == "ALL":
            pass
        return match_found
