from enpyclopedia import *
import logging
import json

# @todo Test Redirects
# Test get_categories()
# Test get_categorymembers()
# Fix pydoc comments in Code

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.ERROR)
enc = Enpyclopedia()
queries = [
    "Potato", # Good page
    "Icelandic_alphabet", # Redirects to Icelandic_orthography
    "https://en.wikipedia.org/wiki/Icelandic_orthography", # Good page
    "https://en.wikipedia.org/wiki/Icelandic_script" # Bad, doesn't exist
]
for elem in queries:
    pg = enc.find(elem)
    if not pg:
        logging.error("No results found for page '%s' .", elem)
    wiki = enc.pages[enc.last_page_index]
    redir = is_redirecting(wiki)
    if redir:
        print(f"The page {wiki.title} is actually redirecting to {redir}.")
    summary = get_summary(wiki_page=wiki)
    if not summary:
        logging.error("Could not retrieve the summary of page '%s' .", elem)
        exit(1)
    print(wiki.title)
    print(summary)

    langlinks = get_other_languages(wiki_page=wiki)

    if not langlinks:
        logging.info("No other languages were found for page '%s' .", elem)
        exit(1)
    txt = get_wiki_text(wiki_data=wiki) # Implicitly imported function, "txt" type by default
    if txt == None:
        logging.error("An error ocurred retrieving the text of page '%s' .", elem)
        exit(1)
    wikitxt = get_wiki_text(wiki_data=wiki, type="wikitext")
    if txt == None:
        logging.error("An error ocurred retrieving the text of page '%s' with type 'wikitext'.", elem)
        exit(1)

    sections = get_sections(wiki_page=wiki)
    if sections == None:
        logging.error("Error encountered.") # This error is logged on the get_sections() function, so no need to do it twice
        exit(1)
    print(sections)
    for s in sections:
        txt = get_wiki_text(s, type="text")
        # Logically, either one of these fail, or none fail, because a wikipedia page MUST have both of these
        if txt == None: 
            logging.error("An error ocurred retrieving the text of section '%s' with type 'wikitext'.", s.title)
            exit(1)
        print(txt)
        print(get_wiki_text(s, type="wikitext"))
    categories = get_categories(wiki_page=wiki)
    print(categories)
    for cat in categories:
        print("PAGES IN CATEGORY: ", cat.title)
        index = 1
        for m in get_category_members(wiki_category=cat, cmlimit=10, cmsort="timestamp", cmdir="desc"):
            print(index, m.title)
            index += 1
        index = 1
        print("SUBCATEGORIES IN CATEGORY: ", cat.title)
        for sc in get_category_members(wiki_category=cat, cmlimit=5, cmtype="subcat"):
            print(index, sc.title)
            index += 1


    pages  = get_all_pages(wiki_page=wiki)
    for p in pages:
        print(p.title)

    get_all_imgs(wiki)
