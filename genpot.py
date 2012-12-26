import os

from fabricate import *

def build():
    genpot()

def genpot():
    fs = os.listdir("views")
    tpls = filter(lambda f: os.path.splitext(f)[1] == ".tpl", fs)
    for tpl in tpls:
        tplpath = os.path.join("views", tpl)
        root, ext = os.path.splitext(tpl)
        potdir = "locale/_pot"
        potname = root + ".pot"
        run('python', 'i18n/pygettext.py', '-p', potdir, '-o', potname, tplpath)

def clean():
    autoclean()

main()
