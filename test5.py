import socket
from urllib import parse
import os
from threading import Thread
import re

isInFolder = False
folderName = ""
def sendRequest(client,url):
    """ Send HTTP request to sever """
    host =  url.replace("http://","")

    #Ex: http://example.com
    if host.find("/") == -1: #there is no resource
        resource = "/index.html"
    #Ex: http://example.com/
    elif host[host.find("/"):] == '/':
        host = host.split("/")[0]
        resource = "/index.html"
    else:
        host = host.split("/")[0]
        resource = url.replace("http://","")
        resource = resource[resource.find("/"):]

        #HTTP Request
        request = 'GET {} HTTP/1.1\r\nHost: {}\r\nConnection: Keep-Alive\r\n\r\n'.format(resource,host)
        client.sendall(request.encode())

def readHeader(client):
    """ Read the header of HTTP response """
    data = b''
    chunk_size = 1
    try:
        while b'\r\n\r\n' not in data:
            chunk = client.recv(chunk_size)
            if not chunk:
                break
            data += chunk
    except socket.timeout:
        pass
    return data

def readContentLength(client,contentLength):
    """ Read the content of HTTP response in Content-Length form """
    data = b''
    chunk_size = 16000
    length = 0
    try:
        while  contentLength >= length: 
            chunk = client.recv(chunk_size)
            if not chunk:
                break
            data += chunk
            length += len(chunk)
    except socket.timeout:
        pass
    return data

def readTransferEncoding(client):
    """ Read the content of HTTP response in Transfer-Encoding: Chunked form """
    content = b''
    while True:
        chunk_size = b''
        temp = b''
        while b'\r\n' not in chunk_size:
            temp = client.recv(1)
            chunk_size += temp
            
        chunk_size = int(chunk_size.decode(),16)
        if chunk_size == 0:
            break
        chunk = b''
        data = b''
            
        chunk = client.recv(chunk_size)
        data += chunk
        
        chunk = client.recv(2)
        content += data
            
    return content

def separate(data):
    '''Separate header and content. '''
    try:
        index = data.index(b'\r\n\r\n')
    except:
        return (data, bytes())
    else:
        index += len(b'\r\n\r\n')
        return (data[:index], data[index:])
    
def getContentLength(header):
    '''Return value of Content-Length. Otherwise returns 0.'''
    for line in header.split(b'\r\n'):
        if b'Content-Length:' in line:
            return int(line[len(b'Content-Length:'):])
    return 0

def getTransferEncoding(header):
    """ Return true if header have Transfer-Encoding: chunked """
    for line in header.split(b'\r\n'):
        if b'Transfer-Encoding: chunked' in line:
            return True
    return False

def receiveResponse(client):
    """ Return header and content of response """
    header = bytes()
    content = bytes()
    # read until at end of header
    data = readHeader(client)

    # separate our content and header
    header, content = separate(data) 

    # get the Content-Length from the header
    contentLength = getContentLength(header)

    # check Transfer-Encoding: chunked in the header
    transferEncoding = getTransferEncoding(header)

    #Download file Transfer-Encoding: chunked
    if transferEncoding:
        content += readTransferEncoding(client)
    # Download file Content-Length
    else:
        # read until end of Content Length
        content += readContentLength(client,contentLength)

    return (header.decode(),content)

def download(client,url):
    sendRequest(client,url)
    header,content = receiveResponse(client)
    #downloadFile(client,url,content)
    print(header)
    

def downloadFolder(client,data,url):
    allFile = []
    my_dict = re.findall('(?<=<a href=")[^"]*', data.decode('utf8'))
    sub = ''
    for x in my_dict:
    #print(x, end = " \n")
    # simple skip page bookmarks, like #about
        if x[0] == '#':
            continue
        if x[0] =='?':
            continue
    # simple control absolute url, like /about.html
    # also be careful with redirects and add more flexible
    # processing, if needed
        if x[0] == '/':
            sub = url + sub
            continue
        else:
            x = sub + x
            
        url = x
        allFile.append(url)
    
    numberThread = []
    for i in range(0,len(allFile)):
        numberThread.append(Thread(target=download, args=(client,allFile[i],)))
    for i in numberThread:
        i.start()
    for i in numberThread:
        i.join() 

def downloadFile(client,url,data):
    global isInFolder
    global folderName
    downloadDir = os.getcwd()
    host =  url.replace("http://","")
    if host.find("/") == - 1 or host[host.find("/"):] == "/":
        filename = "index.html"
    elif url[-1] == "/" and isInFolder == False: #download folder
        isInFolder = True
        folderName = url.split("/")[-2]
        path = os.path.join(downloadDir, folderName)
        isExit = os.path.exists(path)
        if not isExit:
            os.makedirs(path)#tao thu muc dan den
        downloadFolder(client,data,url)
        print("All file are saved in " + path)
        return
    else:
        filename = url.split("/")[-1]
        filename = filename.replace(" ","_")

    if(isInFolder == True):
        path = downloadDir +"\\" + folderName + "\\" + filename
        print("Saving to " + path)
        file = open(path, 'wb') 
        file.write(data)
        file.close()
    else:
        path = downloadDir + "\\" + filename
        print("Saving to " + path)
        file = open(path, 'wb') 
        file.write(data)
        file.close()
        print("Downloaded !")
        
def connect(client,url,host):
        
    print("Client connected to web server Ip: " + host)
    print("----------------------------------------------")
    download(client,url)

URL = input("Input url: ")
PORT = 80
split_url = parse.urlsplit(URL)
#Get ip 
HOST = socket.gethostbyname(split_url.netloc)
client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect((HOST,PORT))
client.settimeout(5)
connect(client,URL,HOST)

client.close()