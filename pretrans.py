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
    entries = [polib.POEntry(msgid=k, msgstr=d[k]) for k in sorted(d.keys())]
    po = polib.POFile()
    po.extend(entries)
    return po

def updatepo(po, keys):
    print("    {0}% translated.".format(po.percent_translated()))
    d = po2dict(po)
    oldkeys = [k for k in d if k not in keys]
    newkeys = [k for k in keys if k not in d]
    changed = False
    if oldkeys:
        print("    Removing deprecated messages...")
        for k in oldkeys:
            print("      {0}".format(repr(k)))
        # Removing deprecated messages.
        d = {k: d[k] for k in d if k in keys}
        changed = True
    if newkeys:
        print("    Adding new messages...")
        for k in newkeys:
            print("      {0}".format(repr(k)))
        # Adding new messages to be translated.
        d.update({k: "" for k in keys if k not in d})
        changed = True
    po = dict2po(d)
    if changed:
        print("    {0}% translated.".format(po.percent_translated()))
    return po

if __name__ == "__main__":
    import os

    langs = os.listdir("locale")
    langs.remove("README")
    fs = os.listdir("views")
    ptps = filter(lambda f: os.path.splitext(f)[1] == ".ptp", fs)
    views = list(map(lambda f: os.path.splitext(f)[0], ptps))
    viewkeys = {}
    for view in views:
        print("Creating template for view '{0}'...".format(view))
        ptppath = os.path.join("views", view + ".ptp")
        tplpath = os.path.join("views", view + ".tpl")
        f = open(ptppath, "r")
        sptp = f.read()
        f.close()
        stpl, keys = tpl_and_keys(sptp)
        f = open(tplpath, "w")
        f.write(stpl)
        f.close()
        print("  {0} messages found.".format(len(keys)))
        viewkeys[view] = keys
    for lang in langs:
        print("lang: {0}...".format(lang))
        msgdir = os.path.join("locale", lang, "LC_MESSAGES")
        for view in views:
            print("  Updating PO file for view '{0}'...".format(view))
            popath = os.path.join(msgdir, view + ".po")
            pof = polib.pofile(popath)
            pof = updatepo(pof, viewkeys[view])
            pof.save(popath)
