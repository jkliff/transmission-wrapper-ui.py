#!env python

import web
import subprocess

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


app = web.application (urls, globals())

HOST = 'ssh torrents@svpnproxy'
TRANS = 'transmission-remote --auth=transmission:transmission'

def render (status):
    return TEMPLATE % {'list': status}

def transmission (cmd):
    cmd = '%s %s %s' % (HOST, TRANS, cmd)
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
    return status ()

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
        if cmd is None or cmd == '':
            cmd = 'status'

        if cmd not in CMDS:
            return 'wrong'

        return CMDS [cmd] ()

if __name__ == '__main__':
    app.run()
