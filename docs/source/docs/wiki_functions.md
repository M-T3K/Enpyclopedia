# Wikipedia Functions

The following functions to work with Wikipedia are currently available in Enpyclopedia:

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