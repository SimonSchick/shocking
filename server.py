import BaseHTTPServer
import socketserver
import ssl
import socket
import rf

auth = 'test'

maxLevel = 20

commandMap = {
        "shock": rf.CMD_SHOCK,
        "beep": rf.CMD_BEEP,
        "vibrate": rf.CMD_BUZZ
}

file = open('index.html', 'rb')
html = file.read()
file.close()

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
        def do_GET(s):
                s.send_response(200)
                s.applyHeaders()
                s.send_header("Content-Type", "text/html; charset=utf-8")
                s.end_headers()
                s.wfile.write(html)

        def applyHeaders(s):
                s.send_header("Access-Control-Allow-Origin", "*")
                s.send_header("Access-Control-Allow-Headers", "authorization")

        def do_OPTIONS(s):
                s.send_response(200)
                s.applyHeaders()
                s.end_headers()
        def do_POST(s):
                print(s.headers.getheader('x-user'))
                authHeader = s.headers.getheader('authorization')
                if not authHeader or authHeader != 'Bearer ' + auth:
                        s.send_response(401)
                        s.applyHeaders()
                        s.end_headers()
                        return
                data = s.rfile.read(int(s.headers.getheader('content-length') or '0'))
                if len(data) == 0:
                        s.send_response(400)
                        s.applyHeaders()
                        s.end_headers()
                        return
                split = data.split(',')
                rf.sendFor(1000, commandMap[split[0]], min(int(split[1]), maxLevel))
                s.send_response(200)
                s.applyHeaders()
                s.end_headers()

class HTTPServerV6(BaseHTTPServer.HTTPServer):
    address_family = socket.AF_INET6

httpd = HTTPServerV6(('::', 443), MyHandler)

httpd.socket = ssl.wrap_socket(httpd.socket, 
        keyfile="./key.pem", 
        certfile='./cert.pem', server_side=True)

httpd.serve_forever()