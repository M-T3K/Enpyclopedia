from enpyclopedia import Enpyclopedia
import logging

logging.basicConfig(level=logging.INFO)
enc = Enpyclopedia()
enc.find("Potato")
pg = enc.find("https://en.wikipedia.org/wiki/Potato")
if pg == None:
    exit(0)
wiki = enc.pages[enc.last_page_index]
redir = wiki.is_redirect()
summary = wiki.get_summary()
print(wiki.args["title"])
print(summary)

langlinks = wiki.get_other_languages()
txt = wiki.get_full_text() # Implicitly obtains in a "text" format
wikitxt = wiki.get_full_text(type="wikitext")

sections = wiki.get_sections()
print(sections)
for s in sections:
    print(s.get_text(type="text"))
    print(s.get_text(type="wikitext"))

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