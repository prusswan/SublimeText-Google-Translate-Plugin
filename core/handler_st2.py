#!/usr/bin/python
# coding:utf-8
# https://github.com/MtimerCMS/SublimeText-Google-Translate-Plugin



import sublime
import os
import sys
import imp

st_version = 2
if int(sublime.version()) > 3000:
    st_version = 3

arch_lib_path = None
if sublime.platform() == 'linux':
    # arch_lib_path = os.path.join(os.path.dirname(__file__), 'lib',
    arch_lib_path = os.path.join(sublime.packages_path(), 'Inline Google Translate', 'lib',
        'st%d_linux_%s' % (st_version, sublime.arch()))
    print('SFTP: enabling custom linux ssl module')
    for ssl_ver in ['1.0.0', '10', '0.9.8']:
        lib_path = os.path.join(arch_lib_path, 'libssl-' + ssl_ver)
        sys.path.append(lib_path)
        print(lib_path)
        try:
            import _ssl
            print('SFTP: successfully loaded _ssl module for libssl.so.%s' % ssl_ver)
            break
        except (ImportError) as e:
            print('SFTP: _ssl module import error - ' + str(e))
    if '_ssl' in sys.modules:
        try:
            if sys.version_info < (3,):
                plat_lib_path = os.path.join(sublime.packages_path(), 'Inline Google Translate',
                    'lib', 'st2_linux')
                m_info = imp.find_module('ssl', [plat_lib_path])
                m = imp.load_module('ssl', *m_info)
            else:
                import ssl
        except (ImportError) as e:
            print('SFTP: ssl module import error - ' + str(e))

import urllib2
import httplib

from socks_st2 import *

class SocksiPyConnection(httplib.HTTPConnection):
    def __init__(self, proxytype, proxyaddr, proxyport=None, rdns=True, username=None, password=None, *args, **kwargs):
        self.proxyargs = (proxytype, proxyaddr, proxyport, rdns, username, password)
        httplib.HTTPConnection.__init__(self, *args, **kwargs)

    def connect(self):
        self.sock = socksocket()
        self.sock.setproxy(*self.proxyargs)
        if type(self.timeout) in (int, float):
            self.sock.settimeout(self.timeout)
        self.sock.connect((self.host, self.port))

class SocksiPyConnectionS(httplib.HTTPConnection):
    def __init__(self, proxytype, proxyaddr, proxyport=None, rdns=True, username=None, password=None, *args, **kwargs):
        self.proxyargs = (proxytype, proxyaddr, proxyport, rdns, username, password)
        httplib.HTTPConnection.__init__(self, *args, **kwargs)

    def connect(self):
        sock = socksocket()
        sock.setproxy(*self.proxyargs)
        if type(self.timeout) in (int, float):
            sock.settimeout(self.timeout)
        sock.connect((self.host, self.port))
        # self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file)

class SocksiPyHandler(urllib2.HTTPHandler, urllib2.HTTPHandler):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kw = kwargs
        urllib2.HTTPHandler.__init__(self)

    def http_open(self, req):
        def build(host, port=None, strict=None, timeout=0):
            conn = SocksiPyConnection(*self.args, host=host, port=port, strict=strict, timeout=timeout, **self.kw)
            return conn
        return self.do_open(build, req)

    def https_open(self, req):
        def build(host, port=None, strict=None, timeout=0):
            conn = SocksiPyConnectionS(*self.args, host=host, port=port, strict=strict, timeout=timeout, **self.kw)
            return conn
        return self.do_open(build, req)
