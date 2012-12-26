import gettext

from bottle import route, view, static_file, run

@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root='static')

@route('/')
@view('login')
def login():
    t = gettext.translation("login", "locale", ['pt-br'])
    return {'_': t.lgettext}

run(host='localhost', server='tornado', debug=True, reloader=True)
