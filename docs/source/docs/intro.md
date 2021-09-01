# Introduction

Enpyclopedia is a Python API to use with online encyclopedias such as Wikipedia and Omniglot.
The goal of this software is to provide as much functionality as possible while keeping code simple. In this section, two things will be covered: **installation** and **basic usage**, including **how to log additional information** such as REST Request URIs.


## Installation

You are going to need **Python 3.7** or above to use Enpyclopedia. If you don't know how to install it, you can check [the pyhon website](https://docs.python.org/3/using/index.html) for detailed information depending on your OS.

It's important to use an official copy of python, or otherwise pip may not be installed automatically. Pip is the package manager for python. More information is available [here](https://pip.pypa.io/en/stable/getting-started/).

Since a pip package isn't available just yet, you can download Enpyclopedia by cloning the repository:

`git clone https://github.com/M-T3K/Enpyclopedia.git`

You can then install all required dependencies with `pip install -r requirements.txt`. It's recommended that you create and use a Virtual Environment beforehand.

## Basic Usage

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