import re

import polib

keyre = re.compile(r"\[\[([^]]*)\]\]")

def tpl_and_keys(s):
    spl = keyre.split(s)
    tpl = spl.pop()
    keys = []
    while spl:
        key = spl.pop()
        tpl = spl.pop() + "{{_('" + key + "')}}" + tpl
        keys.append(key)
    return tpl, list(reversed(keys))

def po2dict(po):
    d = {e.msgid: e.msgstr for e in po}
    return d

def dict2po(d):
    entries = [polib.POEntry(msgid=k, msgstr=d[k]) for k in d]
    po = polib.POFile()
    po.extend(entries)
    return po

def updatepo(po, keys):
    d = po2dict(po)
    keys = filter(lambda k: k not in d, keys)
    entries = [polib.POEntry(msgid=k) for k in keys]
    po.extend(entries)
    return po

if __name__ == "__main__":
    import os

    fs = os.listdir("views")
    ptps = filter(lambda f: os.path.splitext(f)[1] == ".ptp", fs)
    langs = os.listdir("locale")
    langs.remove("_pot")
    langs.remove("README")
    for ptp in ptps:
        ptppath = os.path.join("views", ptp)
        tplpath = os.path.join("views", os.path.splitext(ptp)[0] + ".tpl")
        f = open(ptppath, "r")
        sptp = f.read()
        f.close()
        stpl, keys = tpl_and_keys(sptp)
        f = open(tplpath, "w")
        f.write(stpl)
        f.close()
        for lang in langs:
            msgdir = os.path.join("locale", lang, "LC_MESSAGES")
            fs = os.listdir(msgdir)
            pos = filter(lambda f: os.path.splitext(f)[1] == ".po", fs)
            for po in pos:
                popath = os.path.join(msgdir, po)
                pof = polib.pofile(popath)
                updatepo(pof, keys)
                pof.save(popath)
