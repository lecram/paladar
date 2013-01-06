import os
import codecs
import json

import polib

METADATA = {
    'Project-Id-Version': '1.0',
    'MIME-Version': '1.0',
    'Content-Type': 'text/plain; charset=UTF-8',
    'Content-Transfer-Encoding': '8bit',
}

fs = os.listdir("views")
ptps = filter(lambda f: os.path.splitext(f)[1] == ".ptp", fs)
views = list(map(lambda f: os.path.splitext(f)[0], ptps))
f = codecs.open("locale/languages.json", mode="r", encoding="utf8")
langs = json.load(f)
f.close()
del langs['en']
for lang in langs:
    print("lang: {0}...".format(lang))
    msgdir = os.path.join("locale", lang, "LC_MESSAGES")
    for view in views:
        print("  Generating MO file for view '{0}'...".format(view))
        popath = os.path.join(msgdir, view + ".po")
        mopath = os.path.join(msgdir, view + ".mo")
        pof = polib.pofile(popath, encoding="utf-8")
        print("    {0}% translated.".format(pof.percent_translated()))
        pof.metadata = METADATA
        pof.save_as_mofile(mopath)
