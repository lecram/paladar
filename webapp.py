import os
import gettext

from bottle import route, post, redirect, view, static_file, request, run

import cryptacular.core
import cryptacular.pbkdf2
import cryptacular.bcrypt

import peewee

import model

pbkdf2 = cryptacular.pbkdf2.PBKDF2PasswordManager()
bcrypt = cryptacular.bcrypt.BCRYPTPasswordManager()
delegator = cryptacular.core.DelegatingPasswordManager(preferred=pbkdf2, fallbacks=(bcrypt,))

DEFAULT_LANG = 'en'
LANGS = [DEFAULT_LANG]
LANGS.extend(os.listdir("locale"))
LANGS.remove("README")

def lang_from_header(accept_language, available=LANGS, default=DEFAULT_LANG):
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

def get_underline(domain, lang):
    try:
        t = gettext.translation(domain, "locale", [lang])
        _ = t.gettext
    except FileNotFoundError:
        _ = lambda s: s
    return _

@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root='static')

@route('/login')
@view('login')
def login():
    lang = request.query.lang
    if lang not in LANGS:
        lang = lang_from_header(request.headers.get("Accept-Language", ""))
    _ = get_underline("login", lang)
    return dict(_=_, lang=lang)

@post('/login')
def login_submit():
    username = request.forms.get('username')
    password = request.forms.get('password')
    model.paladar_db.connect()
    try:
        user = model.User.get(model.User.handle == username)
    except peewee.DoesNotExist:
        user = None
    if user is None:
        redirect('/login')
    ok = delegator.check(user.hashed_password, password)
    if not ok:
        redirect('/login')
    return "Welcome {0}!".format(user.name)

run(host='localhost', server='tornado', debug=True, reloader=True)
