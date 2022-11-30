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
        self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.client.connect((self.host,self.port))
    
    def sendRequest(self,url):
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
        
        self.client.settimeout(100)
        #HTTP Request
        request = 'GET {} HTTP/1.1\r\nHost: {}\r\nConnection: Keep-Alive\r\n\r\n'.format(resource,host)
        self.client.sendall(request.encode())

    def readHeader(self):
        """ Read the header of HTTP response """
        data = b''
        buffer_size = 1
        try:
            while b'\r\n\r\n' not in data:
                chunk = self.client.recv(buffer_size)
                if not chunk:
                    break
                data += chunk
        except socket.timeout:
            pass
        return data

    def readContentLength(self,contentLength):
        """ Read the content of HTTP response in Content-Length form """
        data = b''
        buffer_size = 16000
        length = 0
        try:
            while  contentLength >= length: 
                chunk = self.client.recv(buffer_size)
                if not chunk:
                    break
                data += chunk
                length += len(chunk)
        except socket.timeout:
            pass
        return data

    def readTransferEncoding(self):
        """ Read the content of HTTP response in Transfer-Encoding: Chunked form """
        content = b''
        while True:
            chunk_size = b''
            temp = b''
            #Receive chunk size
            while b'\r\n' not in chunk_size:
                temp = self.client.recv(1)
                chunk_size += temp
            chunk_size = int(chunk_size.decode(),16)
            #End of content
            if chunk_size == 0:
                break

            chunk = b''
            data = b''
            #Receive chunk by chunk size
            chunk = self.client.recv(chunk_size)
            data += chunk
            #Receive \r\n at the end of chunk
            chunk = self.client.recv(2)
            content += data
            
        return content

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

    def receiveResponse(self):
        """ Return header and content of response """
        header = bytes()
        content = bytes()

        # read until at end of header
        data = self.readHeader()

        # separate our content and header
        header, content = self.separate(data) 

        # get the Content-Length from the header
        contentLength = self.getContentLength(header)

        # check Transfer-Encoding: chunked in the header
        transferEncoding = self.getTransferEncoding(header)

        #Download file Transfer-Encoding: chunked
        if transferEncoding:
            content += self.readTransferEncoding()
        # Download file Content-Length
        else:
            content += self.readContentLength(contentLength)

        return content
    
    def download(self, url):
        """Send request to server and receive response then download"""
        self.sendRequest(url)
        content = self.receiveResponse()
        self.downloadFile(url,content)
    
    def downloadFolder(self,data):
        """Analysis file html to get urls then download them"""
        allFile = []
        #Get name file in tag href in html
        my_dict = re.findall('(?<=<a href=")[^"]*', data.decode('utf8'))
        sub = ''
        for x in my_dict:
        # simple skip page bookmarks, like #about
            if x[0] == '#':
                continue
            if x[0] =='?':
                continue
        # simple control absolute url, like /about.html
            if x[0] == '/':
                sub = self.url + sub
                continue
            else:
                x = sub + x
            
            url = x
            allFile.append(url)
            
        for i in range(0,len(allFile)):
            Thread(target=self.download, args=(allFile[i],)).start()
        
            
    
    def downloadFile(self,url,data):
        """Download data from server in file"""
        global isInFolder
        global folderName
        downloadDir = os.getcwd()
        host =  url.replace("http://","")

        if host.find("/") == - 1 or host[host.find("/"):] == "/":
            fileName = "index.html"
        elif url[-1] == "/" and isInFolder == False: #Download folder
            isInFolder = True
            folderName = url.split("/")[-2]
            path = os.path.join(downloadDir, folderName)
            isExit = os.path.exists(path)
            if not isExit:
                os.makedirs(path) #Create folder
            self.downloadFolder(data)
            print("All files are saved in " + path)
            return
        else:
            fileName = url.split("/")[-1]
            fileName = fileName.replace(" ","_")

        #Download file in folder
        if(isInFolder == True):
            path = downloadDir +"\\" + folderName + "\\" + fileName
            print("Saved in " + path)
            file = open(path, 'wb') 
            file.write(data)
            file.close()
        #Download file
        else:
            path = downloadDir + "\\" + fileName
            print("Saved in " + path)
            file = open(path, 'wb') 
            file.write(data)
            file.close()
        
    def connect(self):
        self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.client.connect((self.host,self.port))
        print("Client connected to web server Ip: " + self.host + "\n")
        
        self.sendRequest(self.url)
        content = self.receiveResponse()
        self.downloadFile(self.url,content)  


        self.client.close()

    
def firsActivity(URL):
    PORT = 80
    split_url = parse.urlsplit(URL)
    #Get ip 
    HOST = socket.gethostbyname(split_url.netloc)
    client = Client(HOST,PORT,URL)
    client.connect()

def main():
    URL = input("Input urls: ")
    manyURL = URL.split()
    numberURL = len(manyURL)
    numberThread = []
    for i in range(0, numberURL):
        numberThread.append(Thread(target=firsActivity, args=(manyURL[i],)))
    for i in numberThread:
        i.start()
    for i in numberThread:
        i.join()

if __name__ == '__main__':
    main()
    