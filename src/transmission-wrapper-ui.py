#!env python
"""
Simple web ui for transmission-remote.
All commands are executed on a remote host through ssh (for proper functionality public ssh keys must be available on the remote host for the user who is running).

Configuration file format:
(order of lines matters)

TODO: implement http authentication.

--
user@host # to connect on remote host
username/password #for web access
--

"""
import web
import subprocess
import datetime

TRANS = 'transmission-remote --auth=transmission:transmission'

urls = (
    '/(.*)', 'executor',
)

TEMPLATE = """<!doctype html>
<html>

<head><title>Torrents frontend</title></head>

<body>

<h1>Torrent management</h1>

<form action="add">
Add
<input type="text" name="url">
<input type="submit">
</form>


<form action="start">
Start
<input type="text" name="idx">
<input type="submit">
</form>

<form action="stop">
Stop
<input type="text" name="idx">
<input type="submit">

</form>

<form action="remove">
Delete
<input type="text" name="idx">
<input type="submit">

</form>

<a href="/">Refresh</a>
<hr>
<pre>
%(list)s
</pre>
<hr>
at %(now)s
</body>

</html>

"""

def normalize_shell_command (s):

    repl_rules = [
        ('(', '\('),
        (')', '\)')
    ]

    r = s
    for repl in repl_rules:
        r = r.replace(repl [0], repl [1])

    return r

def render (status):
    return TEMPLATE % {'list': status, 'now': datetime.datetime.now()}

def transmission (cmd):
    cmd = '%s %s %s' % (web.ctx.HOST, web.ctx.TRANS, cmd)
    return subprocess.check_output (cmd, shell=True)

def e (c, url):
    for u in url.split (','):
        _ (c % u.strip())

_ = lambda x: render (transmission(x))

def status ():
    return _ ('-l')

def add ():
    url = web.input(url=None)['url']
    _ ('-a "%s"' % normalize_shell_command (url))
    raise web.seeother('/')

def remove():
    url = web.input(url=None)['idx']
    e ('-t %s -r', url)
    raise web.seeother('/')

def start():
    url = web.input(url=None)['idx']
    e ('-t %s -s', url)
    raise web.seeother('/')

def stop():
    url = web.input(url=None)['idx']
    e ('-t %s -S', url)
    raise web.seeother('/')

CMDS = {
    'status':   status,
    'add':      add,
    'remove':   remove,
    'start':    start,
    'stop':     stop
}

class executor:
    def GET (self, cmd):
        if cmd is None or cmd == '':
            cmd = 'status'

        web.header('Content-Type', 'text/html')

        if cmd not in CMDS:
            return 'wrong'

        return CMDS [cmd] ()

def gen_set_globals ():
    """web.py is braindead^H^H^H^H^H^H so simple that makes it retardedly complex to pass simple local-file defined global variables to handlers. way to go for a web framework that has as greatest asset its simplicity, folks."""
    def g (handler):
        web.ctx.HOST = HOST
        web.ctx.TRANS = TRANS
        return handler ()

    return g

if __name__ == '__main__':

    global HOST
    import sys

    if len (sys.argv) != 3:
        sys.stderr.write ('usage: APP port config')
        sys.exit (-1)

    conn = None
    cred = ()

    with (open (sys.argv [2])) as f:
        l = f.readlines()
        conn = l[0].strip()
        cred = tuple ([x.strip() for x in l[1].split ('/')])

    HOST = 'ssh %s' % conn

    app = web.application (urls, globals())
    app.add_processor (gen_set_globals())

    app.run()
