#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys

def printf(format, *args):
    sys.stdout.write(format % args)
    sys.stdout.flush()

import httplib2
import json
from threading import Thread
from time import sleep
import urllib
import re
import urllib.parse
import os
from configparser import ConfigParser

g_All = []

cfg = ''
for i in range(len(sys.argv)):
    if sys.argv[i] == '-cfg':
        cfg = sys.argv[i+1]

# 
g_Config = ConfigParser()
g_Config.read(['vsh.cfg', cfg])

g_Login = g_Config['vk']['login']
g_Password = g_Config['vk']['password']

g_UserID = g_Config['vk']['source']


def parse_cookies(setcookie):
    mycookies = {}
    _cookie_start = True
    _cookie_parametervalue = ""
    _cookie_parameter = ""
    _cookie_name = ""
    _cookie_value = ""
    _cookie_invalue = False

    for i in range(0, len(setcookie)):
        if(setcookie[i] == ';'):
            if(_cookie_start == True):
                mycookies[_cookie_name] = _cookie_value

            _cookie_start = False
            _cookie_parameter = ""
            _cookie_parametervalue = ""
            _cookie_invalue = False
        elif(setcookie[i] == ',' and _cookie_parameter != "expires"):
            _cookie_start = True
            _cookie_name = ""
            _cookie_parameter = ""
            _cookie_parametervalue = ""
            _cookie_value = ""
            _cookie_invalue = False
        elif(setcookie[i] == '=' and not _cookie_invalue):
            _cookie_invalue = True
            if(_cookie_start == True):
                _cookie_name = _cookie_name.strip()
            else:
                _cookie_parameter = _cookie_parameter.strip()
        else:
            if(_cookie_invalue == False):
                if(_cookie_start == True):
                    _cookie_name += setcookie[i]
                else:
                    _cookie_parameter += setcookie[i]
            else:
                if(_cookie_start == True):
                    _cookie_value += setcookie[i]
                else:
                    _cookie_parametervalue += setcookie[i]
    return mycookies


def make_cookies(mycookies):
    retStr = ""
    for cookie in mycookies.keys():
        if(len(retStr) > 0):
            retStr += "; "
        retStr += cookie+"="+mycookies[cookie]
    return retStr


def merge_cookies(mycookies, myck2):
    d2 = {}
    for k in mycookies:
        d2[k] = mycookies[k]
    for k in myck2:
        d2[k] = myck2[k]
    return d2


def dump_file(name, cts):
    with open(name, 'w') as f:
        f.write(cts)
    

def ensure_dir(dirname):
    """
    Ensure that a named directory exists; if it does not, attempt to create it.
    """
    try:
        os.makedirs(dirname)
    except OSError, e:
        if e.errno != errno.EEXIST:
            raise
    
    
def init_dl(h, all, headers):
    global g_All
    g_All = []
    lall = all
    for audio in all:
        localname = './static/music/%s-%s.mp3' % (audio[1], audio[0])
        ensure_dir('./static/music')
        if os.path.isfile(localname):
            audio[2] = localname
            g_All.append(audio)
        else:
            for i in range(2):
                try:
                    # first, get update
                    r,audios = h.request('https://vk.com/al_audio.php', 'POST', headers=headers,
                                         body=urllib.parse.urlencode({'act': 'reload_audio', 'al': 1, 'ids': '%s_%s'%(audio[1],audio[0])}))
                    audios = audios.decode('windows-1251')
                    audios = audios.split('<!json>')
                    if (len(audios) < 2):
                        printf("init_dl(): Failed to download audio %s_%s!\n", audio[1], audio[0])
                        continue
                    audios = audios[1].replace('<!>', '')
                    ll = audios.find('<')
                    if ll >= 0:
                        audios = audios[:ll]
                    audio = json.loads(audios.replace("'", "\"").replace("\\x", "\\u00"))[0]
                    printf("init_dl(): Downloading %s to %s\n", audio[2], localname)
                    r,c = h.request(audio[2], 'GET')
                    with open(localname, 'wb') as f:
                        f.write(c)
                    audio[2] = localname
                    g_All.append(audio)
                    break
                except:
                    time.sleep(10.0)
                    pass # retry
    
    
def VkPullThread(config):
    global g_All

    h = httplib2.Http()
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36',
               'Upgrade-Insecure-Requests': '1'}
    
    while not config.exiting:
        printf("VkPullThread(): Connecting/logging in...\n")
        
        r,c = h.request('https://vk.com/')
        LC = parse_cookies(r['set-cookie'])
        
        c = c.decode('utf-8')
        m = re.search(r'\"https:\/\/login.vk.com\/\?act=login&([^\"]*)\"', c);
        raw_url = m.groups()[0]
        # decode url
        raw_url_parsed = urllib.parse.parse_qs(raw_url)
        ip_h = raw_url_parsed['ip_h'][0]
        lg_h = raw_url_parsed['lg_h'][0]
        
        headers['Cookie'] = make_cookies(LC)
        r,c = h.request('https://login.vk.com/', 'POST', headers=headers,
                    body=urllib.parse.urlencode({'act': 'login', 'to': '', '_origin': 'http://vk.com', 'ip_h': ip_h, 'lg_h': lg_h, 'email': g_Login, 'pass': g_Password, 'expire': ''}))
        LC = merge_cookies(LC, parse_cookies(r['set-cookie']))
        
        headers['Cookie'] = make_cookies(LC)
        redir_url_raw = r['location']
        redir_url_split = redir_url_raw.split('?')
        redir_url_args = urllib.parse.parse_qs(redir_url_split[1])
        redir_url_new = 'https://vk.com/login.php?%s' % (urllib.parse.urlencode({'act': 'slogin', 'to': '', 's': '1', '__q_hash': redir_url_args['__q_hash'][0]}))
        r,c = h.request(redir_url_new, 'GET', headers=headers)
        LC = merge_cookies(LC, parse_cookies(r['set-cookie']))
        
        printf("VkPullThread(): Acquiring cookies...\n")

        while True:
            try:
                printf("VkPullThread(): Pulling playlist...\n")
                """
                audios = vk.post(g_ParseAudio, {"act": "load_audios_silent",
                                                "al": 1,
                                                "gid": 0,
                                                "id": g_UserID,
                                                "please_dont_ddos": 2})
                                                """
                headers['Cookie'] = make_cookies(LC)
                r,audios = h.request('https://vk.com/al_audio.php', 'POST', headers=headers,
                            body=urllib.parse.urlencode({'act': 'load_silent', 'al': 1, 'album_id': -1, 'band': False, 'owner_id': g_UserID}))
                audios = audios.decode('windows-1251')
                # audios looks like this.
                # ?<!>?<!>?<!>?<!>{invalid json}
                audios = audios.split("<!json>")
                if len(audios) < 2 or audios[1].find("{") == -1:
                    audios = None
                    sleep(60.0)
                    break
                else:
                    audios = audios[1].replace("'", "\"").replace("\\x", "\\u00")
                    g_All = json.loads(audios)['list']
                    init_dl(h, g_All, headers)
                    sleep(120.0)
            except:
                # here it usually means that the connection was aborted or smth.
                pass

class VkPullThreadConfig:
    def __init__(self):
        self.exiting = False

g_VkPullThreadConfig = VkPullThreadConfig()
g_VkPullThread = Thread(target=VkPullThread, args=(g_VkPullThreadConfig,))
g_VkPullThread.daemon = True
g_VkPullThread.start()

import tornado.ioloop
import tornado.web

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            f = open("./static/index.html", "rb")
            self.write(f.read())
            f.close()
            self.add_header("Content-Type", "text/html")
            self.set_status(200)
        except:
            self.write("404: File Not Found")
            self.set_status(404)

class PullHandler(tornado.web.RequestHandler):
    def get(self):
        global g_All
        self.write(json.dumps(g_All))
        self.set_status(200)

handlers = [
        (r"/", IndexHandler),
        (r"/pull", PullHandler)
    ]
settings = {"static_path": "static"}

app = tornado.web.Application(handlers, **settings)
app.listen(8192)
tornado.ioloop.IOLoop.instance().start()