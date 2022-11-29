import socket
from urllib import parse
import os
from threading import Thread
import re


isInFolder = False
folderName = ""
class Client:
    def __init__(self,host,port,url):
        self.host = host
        self.port = port
        self.url = url
        
    
    def sendRequest(self,client,url):
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

    def readHeader(self,client):
        """ Read the header of HTTP response """
        data = b''
        chunk_size = 1024
        try:
            while b'\r\n\r\n' not in data:
                chunk = client.recv(chunk_size)
                if not chunk:
                    break
                data += chunk
        except socket.timeout:
            pass
        return data

    def readContent(self,client,contentLength):
        """ Read the content of HTTP response """
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

    def separate(self, data):
        '''Separate header and content. '''
        try:
            index = data.index(b'\r\n\r\n')
        except:
            return (data, bytes())
        else:
            index += len(b'\r\n\r\n')
            return (data[:index], data[index:])

    def getContentLength(self, header):
        '''Return value of Content-Length. Otherwise returns 0.'''
        for line in header.split(b'\r\n'):
            if b'Content-Length:' in line:
                return int(line[len(b'Content-Length:'):])
        return 0

    def getTransferEncoding(self,header):
        """ Return true if header have Transfer-Encoding: chunked """
        for line in header.split(b'\r\n'):
            if b'Transfer-Encoding: chunked' in line:
                return True
        return False

    def receiveResponse(self,client):
        """ Return header and content of response """
        header = bytes()
        content = bytes()
        # read until at end of header
        data = self.readHeader(client)

        # separate our content and header
        header, content = self.separate(data)

        # get the Content-Length from the header
        contentLength = self.getContentLength(header)

        # check Transfer-Encoding: chunked in the header
        transferEncoding = self.getTransferEncoding(header)

        #Download file Transfer-Encoding: chunked
        if transferEncoding:
            pass
        # Download file Content-Length
        else:
            # read until end of Content Length
            content += self.readContent(client,contentLength)

        return (header.decode(),content)
    
    def download(self, client, url):
        self.sendRequest(client,url)
        header, content = self.receiveResponse(client)
        self.downloadFile(client,url,content)
    
    def downloadFolder(self,client,data):
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
                sub = self.url + sub
                continue
            else:
                x = sub + x
            
            url = x
            allFile.append(url)
        for i in range(len(allFile)):
            t = Thread(target=self.download, args=(client,allFile[i]))
            t.start()
            t.join()
            
    
    def downloadFile(self,client,url,data):
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
            self.downloadFolder(client,data)
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
        
    def connect(self):
        client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        client.connect((self.host,self.port))
        client.settimeout(5)
        print("Client connected to web server Ip: " + self.host)
        print("----------------------------------------------")

        self.sendRequest(client,self.url)
        header,content = self.receiveResponse(client)
        self.downloadFile(client,self.url,content)
            
        client.close()

    
def main():
    URL = input("Input url: ")
    PORT = 80
    split_url = parse.urlsplit(URL)
    #Get ip 
    HOST = socket.gethostbyname(split_url.netloc)
    client = Client(HOST,PORT,URL)
    client.connect()

if __name__ == '__main__':
    main()
    