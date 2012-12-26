import os
import gettext

from bottle import route, view, static_file, request, run

DEFAULT_LANG = 'en'
LANGS = [DEFAULT_LANG]
LANGS.extend(os.listdir("locale"))
LANGS.remove("_pot")

def lang_from_header(accept_language, available=LANGS, default='en'):
    accept_language = accept_language.replace(" ", "")
    pairs = []
    for acc in accept_language.split(','):
        sp = acc.split(";q=")
        if len(sp) == 2:
            pairs.append(sp)
        else:
            pairs.append((acc, "1"))
    pairs.sort(key=lambda p: float(p[1]), reverse=True)
    locales = [p[0] for p in pairs]
    for locale in locales:
        for lang in available:
            if locale[:2].lower() == lang[:2].lower():
                return lang
    return default

@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root='static')

@route('/')
@view('login')
def login():
    lang = lang_from_header(request.headers.get("Accept-Language", ""))
    try:
        t = gettext.translation("login", "locale", [lang])
        _ = t.lgettext
    except FileNotFoundError:
        _ = lambda s: s
    return {'_': _}

run(host='localhost', server='tornado', debug=True, reloader=True)
