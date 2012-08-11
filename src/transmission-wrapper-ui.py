#!env python
"""
Configuration file format:
(order of lines matters)
--
user@host # to connect on remote host
username/password #for web access
--

"""
import web
import subprocess

TRANS = 'transmission-remote --auth=transmission:transmission'

urls = (
    '/(.*)', 'executor',
)

TEMPLATE = """
<html>

<body>

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

<hr>
<a href="/">Refresh</a>
<hr>
<pre>
%(list)s

</pre>
</body>

</html>

"""

def render (status):
    return TEMPLATE % {'list': status}

def transmission (cmd):
    cmd = '%s %s %s' % (web.ctx.HOST, web.ctx.TRANS, cmd)
    print cmd
    return subprocess.check_output (cmd, shell=True)

_ = lambda x: render (transmission(x))

def status ():
    return _ ('-l')

def add ():
    url = web.input(url=None)['url']
    _ ('-a "%s"' % url)
    return status ()

def remove():
    url = web.input(url=None)['idx']
    _ ('-t %s -r' % url)
    return status ()

def start():
    url = web.input(url=None)['idx']
    _ ('-t %s -s' % url)
    raise web.seeother('/')

def stop():
    url = web.input(url=None)['idx']
    _ ('-t %s -S' % url)
    return status ()


CMDS = {
    'status':   status,
    'add':      add,
    'remove':   remove,
    'start':    start,
    'stop':     stop
}

class executor:
    def GET (self, cmd):
        print
        if cmd is None or cmd == '':
            cmd = 'status'

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

    web.ctx.HOST = HOST
    app = web.application (urls, globals())
    app.add_processor (gen_set_globals())

    app.run()
