import os
import gettext

import bottle

from beaker.middleware import SessionMiddleware

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

session_opts = {
    # Requires a memcached server.
    'session.type': 'ext:memcached',
    'session.url': 'localhost:11211',
    # Cookie is discarded when browser closes.
    'session.cookie_expires': True,
    # Session will save itself anytime it is accessed.
    'session.auto': True,
    # A lock dir is always required.
    'session.lock_dir': "lock",
    # Enable AES encryption.
    'session.encrypt_key': b'6ugGzf7bv4bb7tfv6VCeHtcGpgZjzzW5',
    'session.validate_key': b'cJ7kQCOPeANksD5J4lFU2lHa2RZaTsBH'
}

app = SessionMiddleware(bottle.app(), session_opts)

def lang_from_header(request, available=LANGS, default=DEFAULT_LANG):
    accept_language = request.headers.get("Accept-Language", "")
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

def get_lang_dict(domain, request):
    session = request.environ.get('beaker.session')
    lang = request.query.lang
    if lang in LANGS:
        user = logged_user(session)
        if user is not None:
            user.language = lang
            user.save()
    else:
        lang = session.get('user_language')
        if lang not in LANGS:
            lang = lang_from_header(request)
    _ = get_underline(domain, lang)
    return dict(_=_, lang=lang)

def logged_user(session):
    username = session.get('user_handle', False)
    if not username:
        return None
    model.paladar_db.connect()
    try:
        user = model.User.get(model.User.handle == username)
    except peewee.DoesNotExist:
        user = None
    return user

@bottle.route('/static/<filename:path>')
def send_static(filename):
    return bottle.static_file(filename, root='static')

@bottle.route('/')
@bottle.view('home')
def home():
    session = bottle.request.environ.get('beaker.session')
    user = logged_user(session)
    if user is None:
        bottle.redirect('/login')
    d = get_lang_dict("home", bottle.request)
    d.update(user=user)
    return d

@bottle.route('/login')
@bottle.view('login')
def login():
    return get_lang_dict("login", bottle.request)

@bottle.post('/login')
def login_submit():
    username = bottle.request.forms.get('username')
    password = bottle.request.forms.get('password')
    model.paladar_db.connect()
    try:
        user = model.User.get(model.User.handle == username)
    except peewee.DoesNotExist:
        user = None
    if user is None:
        bottle.redirect('/login')
    ok = delegator.check(user.hashed_password, password)
    if not ok:
        bottle.redirect('/login')
    session = bottle.request.environ.get('beaker.session')
    session['user_handle'] = username
    session['user_language'] = user.language
    bottle.redirect('/')

@bottle.route('/logout')
def logout():
    session = bottle.request.environ.get('beaker.session')
    session.invalidate()
    bottle.redirect('/login')

bottle.run(app=app, host='localhost', server='tornado', debug=True, reloader=True)
