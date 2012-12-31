import os

import polib

METADATA = {
    'Project-Id-Version': '1.0',
    'MIME-Version': '1.0',
    'Content-Type': 'text/plain; charset=UTF-8',
    'Content-Transfer-Encoding': '8bit',
}

fs = os.listdir("views")
ptps = filter(lambda f: os.path.splitext(f)[1] == ".ptp", fs)
langs = os.listdir("locale")
langs.remove("README")
for lang in langs:
    print("lang: {0}...".format(lang))
    msgdir = os.path.join("locale", lang, "LC_MESSAGES")
    fs = os.listdir(msgdir)
    pos = filter(lambda f: os.path.splitext(f)[1] == ".po", fs)
    for po in pos:
        popath = os.path.join(msgdir, po)
        mopath = os.path.splitext(popath)[0] + ".mo"
        pof = polib.pofile(popath, encoding="utf-8")
        print("  {0}% translated.".format(pof.percent_translated()))
        pof.metadata = METADATA
        pof.save_as_mofile(mopath)
