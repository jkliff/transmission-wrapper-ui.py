#!env python
"""
Simple web ui for transmission-remote.
All commands are executed on a remote host through ssh (for proper functionality public
ssh keys must be available on the remote host for the user who is running).

Configuration file format:
(order of lines matters)

TODO: implement http authentication.

--
user@host # to connect on remote host
username/password #for web access
--

"""
import datetime
import os
import re
import subprocess
import sys
import traceback
import web

TRANS = 'transmission-remote --auth=transmission:transmission'

urls = (
    '/(.*)', 'executor',
)

TEMPLATE = """<?xml version="1.0"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">

<head>
<title>Torrents frontend</title>
<link rel="stylesheet" type="text/css" href="%(CSS_REF)s" media="screen" />
</head>

<body>

<h1>Torrent management</h1>

<div id="canvas">
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

<a href="/" class="command">Refresh</a>
<hr>
<pre>
%(list)s
</pre>
<hr>
at %(now)s
</div>
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
    return TEMPLATE % {'list': status, 'now': datetime.datetime.now(), 'CSS_REF': web.ctx.CSS_REF}

def hide_lines_if_needed (raw_output, allow_raw=False):
    if allow_raw or not os.path.exists (web.ctx.EXCLUSION_LIST_FILE):
        return raw_output

    with (open (web.ctx.EXCLUSION_LIST_FILE)) as f:
        exclusions = f.readlines()
        r = [re.compile ('.*%s.*' % i.strip()) for i in exclusions if i.strip() != '']
        raw = [l for l in raw_output.split ("\n")]
        return "\n".join ([raw[0]] + [l for l in raw [1:-1] if not any ([x.match (l) for x in r])] + [raw [-1]])

def transmission (cmd):
    cmd = '%s %s %s' % (web.ctx.HOST, web.ctx.TRANS, cmd)
    try:
        return subprocess.check_output (cmd, shell=True)
    except subprocess.CalledProcessError:
        traceback.print_exc()
        return 'Error executing command.'

def e (c, url):
    for u in url.split (','):
        _ (c % u.strip())

_ = lambda x, allow_raw=False: render (hide_lines_if_needed (transmission(x), allow_raw=allow_raw))

def status ():
    return _ ('-l', allow_raw=('raw' in web.input(url=None)))

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
    """
web.py is braindead^H^H^H^H^H^H so simple that makes it retardedly complex to pass simple
local-file defined global variables to handlers. way to go for a web framework that has as
greatest asset its simplicity, folks.

"""

    def g (handler):
        web.ctx.HOST = HOST
        web.ctx.TRANS = TRANS
        web.ctx.CSS_REF = external_css_ref
        web.ctx.EXCLUSION_LIST_FILE = TORRENT_EXCLUSION_LIST
        return handler ()

    return g

def main ():
    global HOST, external_css_ref, TORRENT_EXCLUSION_LIST

    if len (sys.argv) < 3:
        sys.stderr.write ('usage: APP port config [exclusion_list]')
        sys.exit (1)

    conn = None
    cred = ()
    conf_path = sys.argv [2]

    with (open (conf_path)) as f:
        l = f.readlines()
        conn = l[0].strip()
        cred = tuple ([x.strip() for x in l[1].split ('/')])
        external_css_ref = l[2].strip()

    if sys.argv[3]:
        TORRENT_EXCLUSION_LIST = os.path.expanduser (sys.argv[3].strip ())
        if not os.path.exists (TORRENT_EXCLUSION_LIST):
            print 'Exclusion path list does not exits at specified path %s' % TORRENT_EXCLUSION_LIST
            sys.exit (1)

    HOST = 'ssh %s' % conn

    app = web.application (urls, globals())
    app.add_processor (gen_set_globals())

    app.run()

if __name__ == '__main__':
    main ()
