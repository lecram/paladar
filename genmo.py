import os

from fabricate import *

def build():
    genmo()

def genmo():
    langs = os.listdir("locale")
    langs.remove("_pot")
    for lang in langs:
        msgdir = os.path.join("locale", lang, "LC_MESSAGES")
        fs = os.listdir(msgdir)
        pos = filter(lambda f: os.path.splitext(f)[1] == "pos", fs)
        for po in pos:
            popath = os.path.join(msgdir, po)
            run('python', 'i18n/msgfmt.py', popath)

def clean():
    autoclean()

main()
