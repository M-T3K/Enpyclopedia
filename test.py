from enpyclopedia import Enpyclopedia

enc = Enpyclopedia()
# enc.find("Potato")
pg = enc.find("https://en.wikipedia.org/wiki/Stack_Overflow")
if pg == None:
    exit(0)
wiki = enc.pages[enc.last_page_index]
redir = wiki.is_redirect()
summary = wiki.get_summary()
# print(summary)

langlinks = wiki.get_other_languages()
txt = wiki.get_full_text()
wikitxt = wiki.get_full_text(type="wikitext")

sections = wiki.get_sections()
print(sections)
for s in sections:
    print(s.get_text(type="text"))
    print(s.get_text(type="wikitext"))