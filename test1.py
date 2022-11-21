import socket
from urllib import parse
import os


class Client:
    def __init__(self,host,port,url):
        self.host = host
        self.port = port
        self.url = url
        self.header = bytes()
        self.content = bytes()
        self.contentLength = 0


    def sendRequest(self,client):
        """ Send HTTP request to sever """
        host =  self.url.replace("http://","")

        #Ex: http://example.com/
        if self.url[-1] == "/":
            host = host.split("/")[0]
            resource = "/index.html"
        #Ex: http://example.com
        elif self.url[-1] == "m":
            resource = "/index.html"
        else:
            host = host.split("/")[0]
            resource = self.url.replace("http://","")
            resource = resource[resource.find("/"):]
            
        
        #HTTP Request
        request = 'GET {} HTTP/1.1\r\nHost: {}\r\nConnection: keep-alive\r\n\r\n'.format(resource,host)
        client.send(request.encode())

    def readHeader(self,client):
        """ Read the header of HTTP response """
        data = b''
        chunk_size = 16000
        try:
            while b'\r\n\r\n' not in data:
                chunk = client.recv(chunk_size)
                if not chunk:
                    break
                data += chunk
        except socket.timeout:
            pass
        return data

    def readContent(self,client):
        """ Read the content of HTTP response """
        data = b''
        chunk_size = 16000
        length = 0

        try:
            while  self.contentLength >= length: 
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
        """ Return true if header have Tranfer-Encoding: chunked """
        for line in header.split(b'\r\n'):
            if b'Transfer-Encoding: chunked' in line:
                return True
        return False

    def receiveResponse(self,client):
        """ Return header and content of response """
        # read until at end of header
        self.data = self.readHeader(client)

        # separate our content and header
        self.header, self.content = self.separate(self.data)

        # get the Content-Length from the header
        self.contentLength = self.getContentLength(self.header)

        # check Transfer-Encoding: chunked in the header
        self.transferEncoding = self.getTransferEncoding(self.header)

        if self.transferEncoding:
            pass
        else:
            # read until end of Content Length
            self.content += self.readContent(client)

        
        

        return (self.header.decode(), self.content)
    
    def downloadFile(self,data):
        downloadDir = os.getcwd()
        if self.url[-1] == "/" or self.url[-1] == "m":
            filename = "index.html"
        else:
            filename = self.url.split("/")[-1]

        path = downloadDir + "\\" + filename
        print("Saving to " + path)
        file = open(path, 'wb') 
        file.write(data)
        file.close()
        
    def connect(self):
        client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        client.connect((self.host,self.port))
        print("Client connected to : " + self.host)
        print("-------------------------------------")
        self.sendRequest(client)

        self.header, self.content = self.receiveResponse(client)
        self.downloadFile(self.content)
            
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
    