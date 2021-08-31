# Enpyclopedia
A Python API to use with online encyclopedias such as Wikipedia and Omniglot.
The goal of this software is to provide as much functionality while keeping code simple.

## Table of Contents

- [Enpyclopedia](#enpyclopedia)
  - [Table of Contents](#table-of-contents)
  - [Usage](#usage)
    - [Installation](#installation)
    - [Basic Usage](#basic-usage)
    - [Logging Additional Information](#logging-additional-information)
  - [Wikipedia](#wikipedia)
    - [Data Structures](#data-structures)
      - [WikipediaEntry Dataclass](#wikipediaentry-dataclass)
      - [WikipediaEntryID Dataclass](#wikipediaentryid-dataclass)
      - [WikipediaEntryPage Dataclass](#wikipediaentrypage-dataclass)
      - [WikipediaSection Dataclass](#wikipediasection-dataclass)
    - [Wikipedia Functions](#wikipedia-functions)
  - [Current Status](#current-status)
  - [Future Updates](#future-updates)

## Usage

### Installation

Currently the only way to install this is through cloning the git repo or downloading the file. You can do so with the following:

`git clone https://github.com/M-T3K/Enpyclopedia.py`

Once Enpyclopedia has several more features, including support for Omniglot, and is no longer in heavy and constant development, I will create a package distribution for pip.

Once the repo is cloned and the source is downloaded, and you are in place, you can install all the required dependencies with `pip install -r requirements.txt`. It's recommended to use a Virtual Environment for this.

### Basic Usage

In this example, you will learn:
- How the Enpyclopedia() object is instantiated.
- How to use this object to find pages, by title or link.
- Check if a specific page exists with the `.find()` method.
- Access any previously accessed page without a new request (requests are expensive!)
- Access all of a page's Request Arguments through the `WikipediaPage` object.

```
from enpyclopedia import Enpyclopedia # First you must import the file
# You may also want to import get_wiki_text if you want to retrieve a page's text.

enc = Enpyclopedia() # Create the Enpyclopedia() object
enc.find("Potato")   # Find a specific page in Wikipedia
page = enc.find("https://en.wikipedia.org/wiki/Potato") # You can also find it using a complete link

# You can also check if a page exists by the return value of the find() method
if not enc.find("Nonsense.garbage.that.makes.no.sense"):
    print("Page does not exist")

# Since all (valid) pages found in the enpyclopedia are stored in memory to avoid additional requests,
same_page = enc.pages[enc.last_page_index] # same_page and page are the same (the last page)

if page.title == same_page.title:
    print("They are the same page!")

```

If you require a bigger example, showing all the features of Enpyclopedia applied to Wikipedia, you can check the [general_wikipedia_test.py](https://www.github.com/M-T3K/Enpyclopedia/blob/main/general_wikipedia_test.py) file.

### Logging Additional Information

You may wish to log more information. For example, you may be interested in printing all requests being made to manually check them and familiarize yourself with the API. You can do so by changing the logging level in your program. *Enpyclopedia* will inherit it. This can be done in the following way:

```
import logging
logging.basicConfig(level=logging.INFO) # This prints additional information
```

## Wikipedia 

### Data Structures

Enpyclopedia contains the following data structures. With the exception of `Enpyclopedia`, they are all [DataClasses](https://docs.python.org/3/library/dataclasses.html).

#### WikipediaEntry Dataclass

A WikipediaEntry dataclass is the most basic data structure in Enpyclopedia for Wikipedia. It contains the following members:
- `ns: int`
- `title: str`

#### WikipediaEntryID Dataclass

A WikipediaEntryID dataclass inherits from the WikipediaEntry dataclass, and thus contains the same attributes and an additional one:
- `pageid: int`

#### WikipediaEntryPage Dataclass

A WikipediaEntryPage Dataclass inherits from the WikipediaEntryID dataclass, and thus contains the same attributes and several additional ones:
- `contentmodel: str`
- `pagelanguage: str`
- `pagelanguagehtmlcode: str`
- `pagelanguagedir: str`
- `touched: str`
- `lastrevid: int`
- `length: int`
- `talkid: int`
- `fullurl: str`
- `editurl: str`
- `canonicalurl: str`

For optimization purposes, additional data that may be required multiple times for functions or for accessing are kept in storage as kind of a cache to avoid additional requests. These are the following:

- `redirects: WikipediaEntryID[] = None`: Not all pages have redirects, but if they do they are automatically stored in this list of [WikipediaEntryID](#wikipediaentryid-dataclass).
- `sections: WikipediaSection[] = None`: Once `get_sections()` is called, they get returned and stored for further use as a list of [WikipediaSection](#wikipediasection-dataclass).
- `categories: WikipediaEntry[] = None`: once `get_categories()` is called, they get returned and stored for further use as a list of [WikipediaEntry](#wikipediaentry-dataclass).
- `html: BeautifulSoup = None`: This contains a BeautifulSoup object to parse the html source of the page. It is used in functions `is_redirecting()` and `get_all_imgs()` and may need to be accessed multiple times. The BeautifulSoup object itself contains the html source. A function `get_html(url: str)` is provided too if you need to obtain this but do not wish to call the aforementioned functions.

#### WikipediaSection Dataclass

A WikipediaSection Dataclass contains all the data regarding a Wikipedia page' sections. Its members are the following:

- `toclevel`
- `level`
- `line`
- `number`
- `index`
- `fromtitle`
- `byteoffset`
- `anchor`

### Wikipedia Functions

The following functions to work with Wikipedia are available in Enpyclopedia:

- `is_redirect(wiki_page: WikipediaEntryPage) -> str`:  Checks wether or not the WikipediaEntryPage is redirecting to another page. A page that is redirecting to another one will not inherit certain fields on a request like Sections.
    - Return: 
        - String containing the name of the page it's redirecting to.
        - `None` if the page isn't redirecting to another one.
- `get_summary(wiki_page: WikipediaEntryPage) -> str`: Retrieves the summary of the page.
    - Return: 
        - String containing the summary of the page (text from the first section).
        - `""` if there's been an error.
- `get_wiki_text(wiki_data: WikipediaEntryPage or WikipediaSection, type: str = "text") -> str`: Retrieves the full text of the Wikipedia Page.
    - Arguments: 
        - Instance of `WikipediaPage` or `WikipediaSection` from which to find text.
        - String `type` that defaults to `text` and can be either `text` or `wikitext`. 
    - Return: 
        - String containing the entire text of the page.
        - `None` if any argument is wrong.
- `get_other_languages(wiki_page: WikipediaEntryPage) -> str[]`: Identifies the links for the same page in all other available languages.
    - Return: 
        - List of Strings containing the links to the page's counterparts in other languages.
        - `[]` if this page is not available in other languages.
- `get_sections(wiki_page: WikipediaEntryPage) -> WikipediaSection[]`: Retrieves all the sections of the current page. If the sections had already been stored previously within the `WikipediaEntryPage`, those are returned instead and no new requests are made. If the page is redirecting to another one, it's possible that no sections will be returned. This is a server-side API limitation Enpyclopedia can only inform of (both here, and thoroughly in the code). If no sections are found, Enpyclopedia will log all relevant information.
    - Return: 
        - List of WikipediaSection in which each element contains all the information regarding a section of the page. The length of the list is equal to the amount of sections in the page.
- `get_categories(wiki_page: WikipediaEntryPage) -> WikipediaEntry[]`: Retrieves all the categories of the current page. If the sections had already been stored previously within the `WikipediaEntryPage`, those are returned instead and no new requests are made.
    - Return: 
        - List of WikipediaEntry in which each element contains the information of the Category. More information on [here](#wikipediaentry-dataclass). The length of the list is equal to the amount of categories the page belongs to.
- `get_category_members(wiki_category: WikipediaEntry, cmlimit: int) -> WikipediaEntryID[]`: It retrieves a certain amount (limited by cmlimit) of pages that belong to a specific category. This WikipediaEntryPage object must be a valid Category for the method to work. 
    - Arguments: 
        - Int `cmlimit` that defaults to `20` that determines the amount of pages to find that belong to a category.
        - Full list of arguments can be found in the following MediaWiki [API page](https://www.mediawiki.org/wiki/API:Categorymembers)
    - Return: 
        - WikipediaEntryID list of `cmlimit` length that contains page information of all the pages that belong to the specific category.
        - `None` if the WikipediaEntryPage that calls this method *is not* a Category.
- `get_all_pages(wiki_page: WikipediaEntryPage, aplimit: int) -> WikipediaEntryPage[]`: It retrieves a certain amount (limited by aplimit) of pages that can be found in the current page.
    - Arguments: 
        - Int `aplimit` that defaults to `10` that determines the amount of pages to find within the page that calls this method.
        - Full list of arguments can be found in the following MediaWiki [API page](https://www.mediawiki.org/wiki/API:Allpages)
    - Return: 
        - WikipediaPage list of `aplimit` length that contains page information of the first `aplimit` number of pages that can be found.
- `get_all_imgs(wiki_page: WikipediaEntryPage, directory: str) -> (int, int)`: Downloads using wget's package all images found in a webpage to the specified directory.
    - Arguments: 
        - String `directory` that defaults to `imgs\` that determines the directory to which to download the page's images. This directory is joined (as per `os.path.join()`) with the title of the WikipediaEntryPage `wiki_page`.
    - Return: 
        - Tuple of integers containing the following (and in this order):
            - Number of images downloaded.
            - Total number of images.
    - Other Important Information: 
        - Has a dependency on the [wget](https://pypi.org/project/wget/) package.
        - Error behaviour is non-blocking: encountering an error *will not* stop the method from attempting to download the rest of the images. Hence, the amount of errors can be calculated by the following:
        ```
        downloads,total = get_all_imgs()
        number_of_errors = total - downloads
        ```

## Current Status

The following features are currently supported:

- [Wikipedia](https://www.wikipedia.org/)
    - [X] Find Page by link or by name
    - [X] Check if page exists (implicit in `.find(page)`)
    - [X] Retrieve page summary
    - [X] Retrieve page in other languages
    - [X] Check if Page is a redirection (For example, [Icelandic Alphabet](https://en.wikipedia.org/wiki/Icelandic_alphabet) redirects to [Icelandic Orthography](https://en.wikipedia.org/wiki/Icelandic_orthography) but other libraries don't detect this, which makes it slightly more difficult to deal with duplicates)
    - [X] Retrieve full text
    - [X] Get page sections
    - [X] Get text from specific section
    - [X] Get page categories
    - [X] Getting all pages from category (category members)
    - [X] Get all other Wikipedia pages that appear in the selected page
    - [X] Get all page images (and download them to a folder)
    - [X] Error logging & Logging of all inner queries
    - [X] Improve Readme file to cover all information
    - [X] Change Objects to DataClasses as per in this [SO question](https://stackoverflow.com/questions/35988/c-like-structures-in-python).

## Future Updates

The following features may be supported in the future:
- General:
    - [ ] Create a ReadTheDocs/Doxygen or whatever (Currently Working on this with Sphinx)
    - [ ] Add thorough testing
- [Wikipedia](https://www.wikipedia.org/)
    - [ ] Select Language of operation for Wikipedia
    - [ ] Get all cited sentences and their correct citation
    - [ ] Allow for batch operations
    - [ ] POST requests
- [Omniglot](https://omniglot.com/)
- [Wolfram](https://www.wolframalpha.com/)
