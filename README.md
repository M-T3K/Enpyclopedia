# Enpyclopedia
A Python API to use with online encyclopedias such as Wikipedia and Omniglot.
The main idea is that the code remains as simple as possible.

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


## Future Updates

The following features may be supported in the future:
- [Wikipedia](https://www.wikipedia.org/)
    - [ ] Get all page images (and download them to a folder)
    - [ ] Get all cited sentences and their correct citation
    - [ ] Allow for batch operations
    - [ ] Select Language of operation for Wikipedia
    - [ ] Get all Links to other Wikipedia pages
    - [ ] Error logging & Logging of all inner queries
- [Omniglot](https://omniglot.com/)
- [Wolfram](https://www.wolframalpha.com/)
