#!/usr/bin/python
# -*- coding: utf-8 -*-

from http.server import BaseHTTPRequestHandler,HTTPServer
import socketserver
import ssl
import socket
import rf
import base64
import json

authMap = {
        "testuser": {
                "password": "yes",
                "capabilities": {
                        "maxLevel": 10,
                        "maxDuration": 1000,
                        "permissions": ["vibrate", "shock", "beep"]
                }
        },
}

units = {
    "display-name": rf.unhexlify('8910'),
}

commandMap = {
        "shock": rf.CMD_SHOCK,
        "beep": rf.CMD_BEEP,
        "vibrate": rf.CMD_BUZZ
}

file = open('index.html', 'r')
html = file.read()
file.close()

rf = rf.ShockController()

class MyHandler(BaseHTTPRequestHandler):
        def requireAuth(s):
                s.send_response(401)
                s.send_header('WWW-Authenticate', 'Basic realm=\"Shocking\"')
                s.end_headers()


        def checkauth(s):
                authHeader = s.headers.get('authorization')
                if not authHeader or not authHeader.startswith('Basic'):
                        print('invalid auth header')
                        s.requireAuth()
                        return False
                split = authHeader.split(' ')
                if len(split) != 2:
                        print('invalid basic auth')
                        s.requireAuth()
                        return False
                decoded = base64.b64decode(split[1]).decode("utf-8").split(':')
                if len(decoded) != 2:
                        print('invalid base64')
                        s.requireAuth()
                        return False
                if not decoded[0] in authMap or authMap[decoded[0]]['password'] != decoded[1]:
                        print('invalid user', decoded)
                        s.requireAuth()
                        return False
                print('authed', decoded)
                return authMap[decoded[0]]

        def do_GET(s):
                profile = s.checkauth()
                if not profile:
                        return
                s.send_response(200)
                s.send_header("Content-Type", "text/html; charset=utf-8")
                s.end_headers()
                s.wfile.write(html.replace('$config$', 'const config = ' + json.dumps({
                        'capabilities': profile['capabilities'],
                        'units': list(units.keys())
                })).encode())

        def do_OPTIONS(s):
                s.send_response(200)
                s.applyHeaders()
                s.end_headers()

        def do_POST(s):
                profile = s.checkauth()
                if not profile:
                        return
                data = s.rfile.read(int(s.headers.get('content-length') or '0'))
                if len(data) == 0:
                        s.send_response(400)
                        s.end_headers()
                        return
                split = data.decode('utf-8').split(',')
                if len(split) != 4 and not split[0] in units or not split[1] in commandMap:
                        s.send_response(400)
                        s.end_headers()
                        return
                caps = profile['capabilities']
                if not split[1] in caps['permissions']:
                        s.send_response(403)
                        s.end_headers()
                        return
                # unit,mode,duration,level
                rf.sendFor(
                        units[split[0]],
                        commandMap[split[1]],
                        min(int(split[2]), caps['maxDuration']),
                        min(int(split[3]), caps['maxLevel'])
                )
                s.send_response(200)
                s.end_headers()

class HTTPServerV6(HTTPServer):
    address_family = socket.AF_INET6

httpd = HTTPServerV6(('::', 443), MyHandler)

httpd.socket = ssl.wrap_socket(httpd.socket, 
        keyfile="./key.pem", 
        certfile='./cert.pem', server_side=True)

httpd.serve_forever()