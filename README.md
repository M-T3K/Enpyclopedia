# Enpyclopedia
A Python API to use with online encyclopedias such as Wikipedia and Omniglot.
The main idea is that the code remains as simple as possible.

## Logging

If you want to log all the requests being made, alongside additional information, you can do so by changing the logging level in your program. *Enpyclopedia* will inherit it. This can be done in the following way:

```
import logging
logging.basicConfig(level=logging.INFO)
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


## Future Updates

The following features may be supported in the future:
- General:
    - [ ] Improve Readme file to cover all information
    - [ ] Add thorough testing
    - [ ] Create a ReadTheDocs
- [Wikipedia](https://www.wikipedia.org/)
    - [ ] Select Language of operation for Wikipedia
    - [ ] Get all cited sentences and their correct citation
    - [ ] Allow for batch operations
    - [ ] POST requests
- [Omniglot](https://omniglot.com/)
- [Wolfram](https://www.wolframalpha.com/)
