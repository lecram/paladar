from bottle import route, view, static_file, run

@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root='static')

@route('/')
@view('login')
def login():
    return {'_': lambda s: s.upper()}

run(host='localhost', server='tornado', debug=True, reloader=True)
