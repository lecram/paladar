import os

from fabricate import *

sources = os.listdir("views")

def build():
    genpot()

def genpot():
    for source in sources:
        tplpath = os.path.join("views", source)
        root, ext = os.path.splitext(source)
        potdir = "locale/_pot"
        potname = root + ".pot"
        run('python', 'i18n/pygettext.py', '-p', potdir, '-o', potname, tplpath)

def clean():
    autoclean()

main()
