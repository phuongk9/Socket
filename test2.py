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
        print("----Request: \n" + request)
        client.send(request.encode())

    def readUntil(self,client,condition,length_start=0, chunk_size=4096):
        """ Reads from the response until the condition returns True. Returns
        an array of bytes read from the socket.
        length is the total number of bytes read """
        data = bytes()
        chunk = bytes()
        length = length_start
        
        
        try:
            while not condition(length, chunk):
                chunk = client.recv(chunk_size)
                if not chunk:
                    break
                else:
                    data += chunk
                    length += len(chunk)
        except socket.timeout:
            pass
        return data

    def separate(cls, data):
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

    def endOfHeader(self, length, data):
        return b'\r\n\r\n' in data

    def endOfContent(self, length, data):
        return self.contentLength <= length

    def receiveResponse(self,client):
        """ Return header and content of response """
        # read until at end of header
        self.data = self.readUntil(client, self.endOfHeader)

        # separate our content and header
        self.header, self.content = self.separate(self.data)

        # get the Content-Length from the header
        self.contentLength = self.getContentLength(self.header)

        print(self.contentLength)
        # check Transfer-Encoding: chunked in the header
        self.transferEncoding = self.getTransferEncoding(self.header)

        if self.transferEncoding:
            pass
        else:
            pass

        
        # read until end of Content Length
        downloadDir = "C:/Users/pc/Downloads"
        if self.url[-1] == "/" or self.url[-1] == "m":
            filename = "index.html"
        else:
            filename = self.url.split("/")[-1]
        print("Saving to " + downloadDir + "/" + filename)
        with open(os.path.join(downloadDir, filename), 'wt') as file:
            while self.contentLength >= len(self.content):
                data = client.recv(4096)
                if not data:
                    break
                file.write(data.decode())
                file.flush()
                os.fsync(file.fileno())
            file.close()

        
    def connect(self):
        client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        client.connect((self.host,self.port))
        print("Client connected to : " + self.host)
        print("-------------------------------------")
        self.sendRequest(client)

        while True:
            self.receiveResponse(client)
            if self.contentLength == len(self.content):
                break
            
            
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
    