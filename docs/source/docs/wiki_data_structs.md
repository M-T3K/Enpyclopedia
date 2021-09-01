# Wikipedia Data Structures

Enpyclopedia contains the following data structures. With the exception of `Enpyclopedia`, they are all [DataClasses](https://docs.python.org/3/library/dataclasses.html).

## WikipediaEntry Dataclass

A WikipediaEntry dataclass is the most basic data structure in Enpyclopedia for Wikipedia. It contains the following members:
- `ns: int`
- `title: str`

## WikipediaEntryID Dataclass

A WikipediaEntryID dataclass inherits from the WikipediaEntry dataclass, and thus contains the same attributes and an additional one:
- `pageid: int`

## WikipediaEntryPage Dataclass

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

## WikipediaSection Dataclass

A WikipediaSection Dataclass contains all the data regarding a Wikipedia page' sections. Its members are the following:

- `toclevel`
- `level`
- `line`
- `number`
- `index`
- `fromtitle`
- `byteoffset`
- `anchor`