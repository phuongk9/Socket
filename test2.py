import socket
import re
url = "http://web.stanford.edu/class/cs143/handouts/"

n = url.find("//")

n += 2
Host =""
while ( url[n]!= '/'):
    Host += url[n]
    n +=1

client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect((Host,80))

resource = url.split("web.stanford.edu")[1]
request = 'GET {} HTTP/1.1\r\nHost: {}\r\nConnection: Keep-Alive\r\n\r\n'.format(resource,Host)
client.sendall(request.encode())
data = client.recv(16000)
print(data.decode())

print("-----------------------------------------------------------------------------------------------------")

my_dict = re.findall('(?<=<a href=")[^"]*', data.decode('utf8'))

sub = ''
for x in my_dict:      
    if x[0] == '#':
        continue
    if x[0] =='?':
        continue
    
    if x[0] == '/':
        sub = url + sub
        continue
    else:
        x = sub + x

    resource = x.split("web.stanford.edu")[1]
    request = 'GET {} HTTP/1.1\r\nHost: {}\r\nConnection: Keep-Alive\r\n\r\n'.format(resource,Host)
    client.sendall(request.encode())
    data = client.recv(16000)
    print(data)
           
    print("-----------------------------------------------------------------------------------------------------")


client.close()
