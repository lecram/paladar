import os

from fabricate import *

def build():
    gentpl()

def gentpl():
    exp = r's/\[\[\([^]]*\)\]\]/{{_("\1")}}/g'
    fs = os.listdir("views")
    ptps = filter(lambda f: os.path.splitext(f)[1] == ".ptp", fs)
    for ptp in ptps:
        ptppath = os.path.join("views", ptp)
        tplpath = os.path.join("views", os.path.splitext(ptp)[0] + ".tpl")
        run('sed', "'" + exp + "'", "<" + ptppath, ">" + tplpath, shell=True)

def clean():
    autoclean()

main()
