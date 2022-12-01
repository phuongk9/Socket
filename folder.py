import socket
from urllib import parse
import os
from threading import Thread
import re
import time

isInFolder = False
folderName = ""
class Client:
    def __init__(self,port,url):
        self.url = url
        self.host = self.getHost(self.url)
        self.port = port
        self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        
    def getHost(self,url):
        host =  url.replace("http://","")
        if host.find("/"):
            host = host.split("/")[0]
        return host          
          
    def sendRequest(self,url):
        """ Send HTTP request to server """
        temp =  url.replace("http://","")

        #Ex: http://example.com or http://example.com/
        if temp.find("/") == -1 or temp[temp.find("/"):] == '/': #there is no resource
            resource = "/index.html"
        else:
            resource = url.replace("http://","")
            resource = resource[resource.find("/"):]
        
        host = self.getHost(url)
        #HTTP Request
        request = 'GET {} HTTP/1.1\r\nHost: {}\r\nConnection: Keep-Alive\r\n\r\n'.format(resource,host)
        try:
            self.client.sendall(request.encode())
            print("Send request to get " + resource + "\n")
        except socket.error:
            print("Request fail... reconnecting\n")
            connected = False  
            self.client.close()
            # recreate socket 
            while not connected:  
                # attempt to reconnect, otherwise sleep for 2 seconds  
                try:  
                    newClient = Client(self.port,self.url)
                    print( "Reconnect successfully\n" ) 
                    newClient.connect() 
                    connected = True                
                except socket.error:  
                    time.sleep(2)  

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
        except socket.error:
            print("Connection lost.... reconnecting\n")
            connected = False  
            self.client.close()
            # recreate socket 
            while not connected:  
                # attempt to reconnect, otherwise sleep for 2 seconds  
                try:  
                    newClient = Client(self.port,self.url)
                    print( "Reconnect successfully\n" ) 
                    newClient.connect() 
                    connected = True               
                except socket.error:  
                    time.sleep(2) 

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
        except socket.error:
            print("Connection lost.... reconnecting\n")
            connected = False  
            self.client.close()
            # recreate socket 
            while not connected:  
                # attempt to reconnect, otherwise sleep for 2 seconds  
                try:  
                    newClient = Client(self.port,self.url)
                    print( "Reconnect successfully\n" ) 
                    newClient.connect()  
                    connected = True              
                except socket.error:  
                    time.sleep(2) 

        return data

    def readTransferEncoding(self):
        """ Read the content of HTTP response in Transfer-Encoding: Chunked form """
        content = b''
        try:
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
                while len(data) != chunk_size:
                    chunk = self.client.recv(chunk_size)
                    data += chunk
                #Receive \r\n at the end of chunk
                chunk = self.client.recv(2)
                content += data
        except socket.timeout:
            pass
        except socket.error:
            print("Connection lost.... reconnecting\n")
            connected = False  
            self.client.close()
            # recreate socket 
            while not connected:  
                # attempt to reconnect, otherwise sleep for 2 seconds  
                try:  
                    newClient = Client(self.port,self.url)
                    print( "Reconnect successfully\n" ) 
                    newClient.connect() 
                    connected = True             
                except socket.error:  
                    time.sleep(2) 

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
       
    def newConnect(self,url):
        newClient = Client(self.port,url)
        newClient.connect()

    def downloadFolder(self,data):
        """Analysis file html to get urls then download them"""
        urls = []
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
            
            urls.append(x)
            
        for i in range(len(urls)):
            Thread(target=self.newConnect, args = (urls[i],)).start()
                             
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
            return
        else:
            fileName = url.split("/")[-1]
            fileName = fileName.replace(" ","_")

        #Download file in folder
        if(isInFolder == True):
            path = downloadDir +"\\" + folderName + "\\" + fileName
            print("Saved in " + path + "\n")
            file = open(path, 'wb') 
            file.write(data)
            file.close()
        #Download file
        else:
            path = downloadDir + "\\" + fileName
            print("Saved in " + path + "\n")
            file = open(path, 'wb') 
            file.write(data)
            file.close()
        
    def connect(self):
        """ Connect to server send request and receive response"""
        try:
            self.client.connect((self.host,self.port))
        except socket.error:
            print("Connection lost... reconnecting")
            connected = False  
            self.client.close()
            # recreate socket 
            while not connected:  
                # attempt to reconnect, otherwise sleep for 2 seconds  
                try:  
                    newClient = Client(self.port,self.url)
                    print( "Reconnect successfully\n" ) 
                    newClient.connect() 
                    connected = True             
                except socket.error:  
                    time.sleep(2) 

        self.client.settimeout(5)
        if isInFolder == False:
            print("Client connected to  " + self.url + " at port " + str(self.port) + "\n")
        
        self.sendRequest(self.url)
        content = self.receiveResponse()
        self.downloadFile(self.url,content)  

        self.client.close()

def firsActivity(URL):
    PORT = 80
    #split_url = parse.urlsplit(URL)
    #Get ip 
    #HOST = socket.gethostbyname(split_url.netloc)
    client = Client(PORT,URL)
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
    