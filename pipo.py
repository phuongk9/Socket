import socket
import select
import os
from urllib import parse
URL = 'http://example.com/index.html'
PORT = 80
split_url = parse.urlsplit(URL)
HOST = socket.gethostbyname(split_url.netloc)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, 80))
s.sendall(b'GET /index.html HTTP/1.1\r\nHOST: example.com\r\n\r\n')

reply = b''
downloadDir = os.getcwd()
while select.select([s], [], [], 3)[0]:
    data = s.recv(16000)
    if not data: break
    reply += data

headers =  reply.split(b'\r\n\r\n')[0]
image = reply[len(headers)+4:]

path = downloadDir + "\\" + "intro1.html"
# save image
f = open(path, 'wb')
f.write(image)
f.close()

