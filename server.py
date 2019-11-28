#!/usr/bin/python
# -*- coding: utf-8 -*-

import BaseHTTPServer
import socketserver
import ssl
import socket
import rf
import base64

authMap = {
}

maxLevel = 3

commandMap = {
        "shock": rf.CMD_SHOCK,
        "beep": rf.CMD_BEEP,
        "vibrate": rf.CMD_BUZZ
}

file = open('index.html', 'rb')
html = file.read()
file.close()

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
        def requireAuth(s):
                s.send_response(401)
                s.send_header('WWW-Authenticate', 'Basic realm=\"Shocking\"')
                s.end_headers()

        def checkauth(s):
                authHeader = s.headers.getheader('authorization')
                if not authHeader or not authHeader.startswith('Basic'):
                        print('invalid auth header')
                        s.requireAuth()
                        return False
                split = authHeader.split(' ')
                if len(split) != 2:
                        print('invalid basic auth')
                        s.requireAuth()
                        return False
                decoded = base64.b64decode(split[1]).split(':')
                if len(decoded) != 2:
                        print('invalid base64')
                        s.requireAuth()
                        return False
                if not decoded[0] in authMap or authMap[decoded[0]] != decoded[1]:
                        print('invalid user', decoded)
                        s.requireAuth()
                        return False
                print('authed', decoded)
                return True

        def do_GET(s):
                if not s.checkauth():
                        return
                s.send_response(200)
                s.send_header("Content-Type", "text/html; charset=utf-8")
                s.end_headers()
                s.wfile.write(html)

        def do_OPTIONS(s):
                s.send_response(200)
                s.applyHeaders()
                s.end_headers()

        def do_POST(s):
                if not s.checkauth():
                        return
                data = s.rfile.read(int(s.headers.getheader('content-length') or '0'))
                if len(data) == 0:
                        s.send_response(400)
                        s.end_headers()
                        return
                split = data.split(',')
                print(split)
                if not split[0] in commandMap:
                        s.send_response(400)
                        s.end_headers()
                        return
                rf.sendFor(1000, commandMap[split[0]], min(int(split[1]), maxLevel))
                s.send_response(200)
                s.end_headers()

class HTTPServerV6(BaseHTTPServer.HTTPServer):
    address_family = socket.AF_INET6

httpd = HTTPServerV6(('::', 443), MyHandler)

httpd.socket = ssl.wrap_socket(httpd.socket, 
        keyfile="./key.pem", 
        certfile='./cert.pem', server_side=True)

httpd.serve_forever()