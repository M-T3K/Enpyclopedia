
from enpyclopedia import Enpyclopedia, get_wiki_text
import logging
import json

logging.basicConfig(level=logging.INFO)
enc = Enpyclopedia()
enc.find("Potato")
pg = enc.find("https://en.wikipedia.org/wiki/Potato")
if pg == False:
    print("Last page does not exist")
wiki = enc.pages[enc.last_page_index]
redir = wiki.is_redirect()
summary = wiki.get_summary()
print(wiki.args["title"])
print(summary)

langlinks = wiki.get_other_languages()
txt = get_wiki_text(wiki_page_or_section=wiki) # Implicitly imported function, "txt" type by default
wikitxt = get_wiki_text(wiki_page_or_section=wiki, type="wikitext")

sections = wiki.get_sections()
print(sections)
for s in sections:
    print(get_wiki_text(s, type="text"))
    print(get_wiki_text(s, type="wikitext"))

categories = wiki.get_categories()
print(categories)
for s in categories:
    print("PAGES IN CATEGORY: ", s.args["title"])
    index = 1
    for m in s.get_category_members(cmlimit=10, cmsort="timestamp", cmdir="desc"):
        print(index, m.args["title"])
        index += 1
    index = 1
    print("SUBCATEGORIES IN CATEGORY: ", s.args["title"])
    for sc in s.get_category_members(cmlimit=5, cmtype="subcat"):
        print(index, sc.args["title"])
        index += 1


pages  = wiki.get_all_pages()
for p in pages:
    print(p.args["title"])

wiki.get_all_imgs()