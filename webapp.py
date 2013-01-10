import os
import codecs
import json
import gettext
import socket

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
f = codecs.open("locale/languages.json", mode="r", encoding="utf8")
LANGS = json.load(f)
f.close()

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

def country_from_environ(request):
    remote_address = request.environ.get("REMOTE_ADDR")
    name, aliases, addresses = socket.gethostbyaddr(remote_address)
    domain = name.split('.')[-1]
    if len(domain) == 2:
        return domain
    else:
        return None

def get_underline(domain, lang):
    try:
        t = gettext.translation(domain, "locale", [lang])
        _ = t.gettext
    except FileNotFoundError:
        _ = lambda s: s
    return _

def get_lang_dict(domain, request):
    session = request.environ.get('beaker.session')
    user = session.get('user')
    # If a language is supplied in the URL, it's used no matter what.
    lang = request.query.lang
    if lang in LANGS:
        # If a user is logged in, supplying a language in the URL changes
        #  the user language on the database.
        if user is not None:
            model.paladar_db.connect()
            user.language = lang
            user.save()
            model.paladar_db.close()
    elif user is not None:
        # If a user is logged in and [s]he doesn't include the language
        #  in the URL, (her|his) prefered language is used.
        lang = user.language
    else:
        # No language in the URL and not logged in?
        # Maybe the browser knows what's the prefered language.
        lang = lang_from_header(request)
    if lang not in LANGS:
        # The last attempt at visitor language guessing is checking if
        #  the ISP domain name has a country code and we have a language
        #  associated with that country in languages.json.
        country = country_from_environ(request)
        if country is not None:
            for key in LANGS:
                if country in LANGS[key]['countries']:
                    lang = key
                    break
    # If everything above fails, the default language will be used.
    _ = get_underline(domain, lang)
    return dict(_=_, lang=lang, langs=LANGS)

def require_login(fail):
    def decorator(f):
        def wrapper():
            model.paladar_db.connect()
            session = bottle.request.environ.get('beaker.session')
            try:
                user = session['user']
            except KeyError:
                bottle.redirect(fail)
            else:
                d = f(user=user)
                d.update(user=user)
                return d
            finally:
                model.paladar_db.close()
        return wrapper
    return decorator

@bottle.route('/static/<filename:path>')
def send_static(filename):
    return bottle.static_file(filename, root='static')

@bottle.route('/')
@bottle.view('home')
@require_login('/login')
def home(user):
    d = get_lang_dict("home", bottle.request)
    return d

@bottle.route('/feeds')
@bottle.view('feeds')
@require_login('/login')
def feeds(user):
    d = get_lang_dict("feeds", bottle.request)
    return d

@bottle.post('/feeds/add')
@require_login('/login')
def feeds_submit(user):
    url = bottle.request.forms.get('url')
    title = bottle.request.forms.get('title')
    description = bottle.request.forms.get('description')
    try:
        channel = model.Channel.get(model.Channel.url == url)
    except peewee.DoesNotExist:
        channel = model.Channel()
        channel.url = url
        channel.type_ = model.ChannelType.get(model.ChannelType.name == "regular")
        channel.title = title
        channel.description = description
        channel.save()
    # TODO: should check if user is already subscribed to channel.
    model.Subscription.create(user=user, channel=channel)
    bottle.redirect('/feeds')

@bottle.route('/about')
@bottle.view('about')
@require_login('/login')
def about(user):
    d = get_lang_dict("about", bottle.request)
    return d

@bottle.route('/login')
@bottle.view('login')
def login():
    d = get_lang_dict("login", bottle.request)
    return d

@bottle.post('/login')
def login_submit():
    username = bottle.request.forms.get('username')
    password = bottle.request.forms.get('password')
    model.paladar_db.connect()
    try:
        user = model.User.get(model.User.handle == username)
    except peewee.DoesNotExist:
        user = None
    model.paladar_db.close()
    if user is None:
        bottle.redirect('/login')
    ok = delegator.check(user.hashed_password, password)
    if not ok:
        bottle.redirect('/login')
    session = bottle.request.environ.get('beaker.session')
    session['user'] = user
    bottle.redirect('/')

@bottle.route('/logout')
def logout():
    session = bottle.request.environ.get('beaker.session')
    session.invalidate()
    bottle.redirect('/login')

bottle.run(app=app, host='localhost', server='tornado', debug=True, reloader=True)
