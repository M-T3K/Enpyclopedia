# Enpyclopedia
A Python API to use with online encyclopedias such as Wikipedia and Omniglot.
The goal of this software is to provide as much functionality while keeping code simple, efficient (as much as python allows...) and data oriented.

## Table of Contents

- [Enpyclopedia](#enpyclopedia)
  - [Table of Contents](#table-of-contents)
  - [Usage](#usage)
    - [Basic Usage](#basic-usage)
    - [Data Structures](#data-structures)
      - [WikipediaPage Object](#wikipediapage-object)
        - [WikipediaPage Members](#wikipediapage-members)
        - [WikipediaPage Request Arguments](#wikipediapage-request-arguments)
          - [Normal Wikipedia Pages](#normal-wikipedia-pages)
          - [Category Wikipedia Pages](#category-wikipedia-pages)
          - [Redirect Wikipedia Pages](#redirect-wikipedia-pages)
        - [WikipediaPage Methods](#wikipediapage-methods)
      - [WikipediaSection Dataclass](#wikipediasection-dataclass)
        - [WikipediaSection Members](#wikipediasection-members)
      - [Additional Functions](#additional-functions)
    - [Logging Additional Information](#logging-additional-information)
  - [Current Status](#current-status)
  - [Future Updates](#future-updates)

## Usage


### Basic Usage

In this example, you can see the following:
- How the Enpyclopedia() object is instantiated.
- How to use this object to find pages, by title or link.
- Check if a specific page exists with the `.find()` method.
- Access any previously accessed page without a new request (requests are expensive!)
- Access all of a page's Request Arguments through the `WikipediaPage` object.

```
import enpyclopedia # First you must import the file

enc = Enpyclopedia() # Create the Enpyclopedia() object
enc.find("Potato")   # Find a specific page in Wikipedia
page = enc.find("https://en.wikipedia.org/wiki/Potato") # You can also find it using a complete link

# You can also check if a page exists by the return value of the find() method
if not enc.find("Nonsense.garbage.that.makes.no.sense"):
    print("Page does not exist")

# Since all (valid) pages found in the enpyclopedia are stored in memory to avoid additional requests,
same_page = enc.pages[enc.last_page_index] # same_page and page are the same (the last page)

if page.args["title"] == same_page.args["title"]:
    print("They are the same page!")

```
### Data Structures

Enpyclopedia contains two fundamental data structures:

- [WikipediaPage](#wikipediapage-object) Class
- [WikipediaSection](#wikipediasection-object) Dataclass

#### WikipediaPage Object

A WikipediaPage object contains all the information for Wikipedia Queries regarding a specific Page.

##### WikipediaPage Members

Each WikipediaPage object contains the following arguments:

- `args`: A dictionary that provides access to dynamic query-dependant arguments called Request Arguments. Detailed information on request arguments is available [here](#wikipediapage-request-arguments).
- `html`: After a GET request that requires the html body of the page is made (either via `is_redirect()` or `get_all_imgs()`) the html body is stored in the `html` member to avoid unnecessary additional requests.
- `redirects`: Not all pages have redirects. If it does, however, they'll be stored in a list of `WikipediaPage`. A list of the request arguments available for categories is [here](#redirect-wikipedia-pages).
- `sections`: Once `get_sections()` is called, the WikipediaPage object stores them in a list of `WikipediaSection`. More information on the WikipediaSection object is available [here](#wikipediasection-object).
- `categories`: Once `get_categories()` is called, the WikipediaPage object stores them in a list of `WikipediaPage`. A list of the request arguments available for categories is [here](#category-wikipedia-pages).

These arguments can be accessed like any other field would in Python:

```
# Assuming previous code is in place
page.argument
```

##### WikipediaPage Request Arguments
To access a page's request arguments, you need to access its `args` member, that operates as a dictionary, in the following way:

```
# Assuming previous code is in place
page.args["name_of_arg"]
```

These request arguments are a copy of the original GET request body in [JSON](https://en.wikipedia.org/wiki/JSON) format once sublists are removed (those can be accessed in other ways). This is the full list of arguments that can be accessed from the `args` dictionary:

###### Normal Wikipedia Pages

Normal Wikipedia Pages will have the following request arguments:
- `pageid`
- `ns`
- `title`
- `contentmodel`
- `pagelanguage`
- `pagelanguagehtmlcode`
- `pagelanguagedir`
- `touched`
- `lastrevid`
- `length`
- `talkid`
- `fullurl`
- `editurl`
- `canonicalurl`

###### Category Wikipedia Pages

Category Wikipedia Pages will have the following request arguments:
    - `ns`
    - `title`

###### Redirect Wikipedia Pages
Redirect Wikipedia Pages will have the following request arguments:
    - `pageid`
    - `ns`
    - `title`

##### WikipediaPage Methods

The following methods are available in the WikipediaPage Object:

- `is_redirect() -> str`: 
    - Return: 
        - String containing the name of the page we've been redirected to.
        - `""` if we haven't been redirected to another page.
- `get_summary() -> str`: 
    - Return: 
        - String containing the summary of the page (text from the first section).
        - `""` if there's been an error.
- `get_other_languages() -> str[]`: 
    - Return: 
        - List of Strings containing the links to the page's counterparts in other languages.
        - `[]` if this page is not available in other languages.
- `get_sections() -> WikipediaSection[]`: 
    - Return: 
        - List of WikipediaSection in which each element contains all the information regarding a section of the page. The length of the list is equal to the amount of sections in the page.
- `get_categories() -> WikipediaPage[]`: 
    - Return: 
        - List of Wikipediapage in which each element contains the information of the Category. More information on [here](#category-wikipedia-pages). The length of the list is equal to the amount of categories the page belongs to.
- `get_category_members(cmlimit: int) -> WikipediaPage[]`: 
    - Arguments: 
        - Int `cmlimit` that defaults to `20` that determines the amount of pages to find that belong to a category.
        - Full list of arguments can be found in the following MediaWiki [API page](https://www.mediawiki.org/wiki/API:Categorymembers)
    - Return: 
        - WikipediaPage list of `cmlimit` length that contains page information of all the pages that belong to the specific category.
        - `[]` if the WikipediaPage that calls this method *is not* a Category.
- `get_all_pages(aplimit: int) -> WikipediaPage[]`: 
    - Arguments: 
        - Int `aplimit` that defaults to `10` that determines the amount of pages to find within the page that calls this method.
        - Full list of arguments can be found in the following MediaWiki [API page](https://www.mediawiki.org/wiki/API:Allpages)
    - Return: 
        - WikipediaPage list of `aplimit` length that contains page information of the first `aplimit` number of pages that can be found.
- `get_all_imgs(directory: str) -> (int, int)`: 
    - Arguments: 
        - String `directory` that defaults to `imgs\` that determines the directory to which to download the page's images.
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

#### WikipediaSection Dataclass

A WikipediaSection Dataclass contains all the data regarding a Wikipedia page' sections.

##### WikipediaSection Members

All WikipediaSection dataclasses will contain the following members that can be accessed like a normal field would be accessed:

- `toclevel`
- `level`
- `line`
- `number`
- `index`
- `fromtitle`
- `byteoffset`
- `anchor`

#### Additional Functions

On top of the methods of the WikipediaPage class, the `get_wiki_text` function takes as part of its arguments an instance of a `WikipediaPage` or `WikipediaSection`, and acts accordingly:

- `get_wiki_text(wiki_page_or_section: WikipediaPage or WikipediaSection, type: str) -> str`: 
    - Arguments: 
        - Instance of `WikipediaPage` or `WikipediaSection` from which to find text.
        - String `type` that defaults to `text` and can be either `text` or `wikitext`. 
    - Return: 
        - String containing the entire text of the page.
        - `""` if the argument `type` is incorrect.

### Logging Additional Information

If you want to log all the requests being made, alongside additional information, you can do so by changing the logging level in your program. *Enpyclopedia* will inherit it. This can be done in the following way:

```
import logging
logging.basicConfig(level=logging.INFO) # This prints additional information
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

## Future Updates

The following features may be supported in the future:
- General:
    - [ ] Add thorough testing
    - [ ] Create a ReadTheDocs/Doxygen or whatever
    - [ ] Change Objects to DataClasses as per in this [SO question](https://stackoverflow.com/questions/35988/c-like-structures-in-python).
- [Wikipedia](https://www.wikipedia.org/)
    - [ ] Select Language of operation for Wikipedia
    - [ ] Get all cited sentences and their correct citation
    - [ ] Allow for batch operations
    - [ ] POST requests
- [Omniglot](https://omniglot.com/)
- [Wolfram](https://www.wolframalpha.com/)
