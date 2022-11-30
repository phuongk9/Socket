import socket
import os
import re
from urllib import parse
import sys
import threading
#Lấy header từ web
def getHead(sock: socket) ->str:
    data = b""
    while True:
        response = sock.recv(1)
        data =data+response
        if "\r\n\r\n" in data.decode(): break
    check = data.decode().find("\r\n\r\n")
    data = data[0:check+4]
    return data
#Lấy Content Length tư server , nếu ko có trả về -1
def getContentLength(temp:str) -> int:
    n = temp.find("Content-Length: ")
    if n ==-1:
        return -1
    index = n+16
    data = temp[index]
    while (data.isdigit()==1):
        index += 1
        data += temp[index]
    return int(data)
#Lấy và lưu vào file index.html với các request gốc
def GetContentLengthHTMLdata(sock: socket, length: int):
    message= b''
    while True:
        data =sock.recv(2048)
        message = message + data
        if len(message) == length:
            break
    f=open('index.html','wb')
    f.write(message)
    f.close()
    return 

#Lấy và lưu vào file với các request tải file có filename
def GetContentLengthData(sock: socket, length: int, filename: str):
    message= b''
    while True:
        data =sock.recv(2048)
        message = message + data
        if len(message) == length:
            break
    f=open(filename,'wb')
    f.write(message)
    f.close()
    return 
#Lấy và lưu dữ liệu của file có transfer encoded: chunked vào index.html có các request gốc
def GetChunkedHTMLData(sock: socket):
    message= b''
    while True:
        data =sock.recv(1024)
        message = message + data
        if b'0\r\n\r\n' in data:
            break
    f=open('index.html','wb')
    f.write(message)
    f.close()
    return 
#Lấy và lưu dữ liệu của file có transfer encoded: chunked vào filename có các request tải file 
def GetChunkedData(sock: socket, filename:str)->str:
    message= b''
    while True:
        data =sock.recv(1024)
        message = message + data
        if b'0\r\n\r\n' in data:
            break
    f=open(filename,'wb')
    f.write(message)
    f.close()
    return message
#Cac ham xu ly chuoi web nhap vao
#Hàm kiểm tra xem có phải request gốc hay không
def checkIndexFile(web :str) ->bool:
    count =0
    for i in web:
        if (i== '/') :
            count +=1
    if ((web[len(web)-1] == '/') and count ==3):
        return True
    else :
        return False
#Ham tim Host cua web
def findHost(web: str) ->str:
    n = web.find("//")
    n = n +2
    Host =""
    while ( web[n]!= '/'):
        Host+=web[n]
        n +=1
    return Host
#Ham tim filename cần tải nếu có filename
def findFileName(web: str) ->str:
    n = len(web)-1
    filename = ''
    while(web[n]!='/'):
        filename = web[n] + filename
        n -=1
    return filename
#ham tao 1 thu muc mơi bên trong folder
def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)
#Ham lấy tên của folder
def getFolderName(web: str)->str:
    n = len(web)-2
    FolderName = ''
    while(web[n]!='/'):
        FolderName = web[n] + FolderName
        n -=1
    return FolderName
#ham lay du lieu và tải xuống các file trong 1 folder

def writeFolderFile(fileName: str, FolderConnectName: str, Host: str, newWeb: str):
    sock1 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock1.connect((Host,80))
    send = "GET " + newWeb+ " HTTP/1.1\r\nHost: " + Host + "\r\n\r\n"
    sock1.sendall(bytes(send.encode()))
    temp = getHead(sock1)
    n = getContentLength(temp.decode()) 
    #Lấy file từ web
    message= b''
    while True:
        data1 =sock1.recv(1024)            
        message = message + data1
        if len(message) == n:
            break
    #Truy cập vào folder để ghi file
    file_dir = os.path.dirname(os.path.realpath('__file__'))
    file_Name = os.path.join(file_dir,FolderConnectName, str(fileName))
    f = open(file_Name,'wb')    
    f.write(message)
    f.close()
    sock1.close()
    return

def getFolderFile(sock: socket, ContentLength: int, web: str, Host: str):
    message = b''
    #Lấy dữ liệu từ web
    while True:
        data = sock.recv(1024)
        message = message + data
        if (len(message) == ContentLength): break
    str_mes = str(message)
    check = 0
    href =0
    AllFileName = []
    count =0
    AllNewWebName = []
    #Tao mot thu muc moi
    FolderName = getFolderName(web)
    FolderConnectName = "./" + FolderName + "/"
    createFolder(FolderConnectName)
    #Tim cac chuoi href có trong data
    href = str_mes.find("href=", check, ContentLength)
    while (href!= -1):
        #Xu ly va luu cac file
        newWeb = web
        check = href +6
        href = href + 6
        fileName = ''
        while(str_mes[href] != '"'):
            fileName+= str_mes[href]
            href = href + 1
        if fileName[0]  =='/':
            fileName = fileName[1:len(fileName)]
        newWeb += '/'+ fileName
        if (fileName.find('.')==-1): #Bo qua cac href khong phải là file cần tải
            href = str_mes.find("href=", check, ContentLength)
            continue
        #connect to file
        AllFileName.append(fileName)
        AllNewWebName.append(newWeb)
        count = count+1
        #writeFile(fileName,FolderConnectName, Host,newWeb).appen
        #find next href

        href = str_mes.find("href=", check, ContentLength)
        
    #Xu ly moi nhieu ket noi HTTP de luu file bang multi thread
    for i in range (count):
        threading.Thread(target = writeFolderFile, args = (AllFileName[i],FolderConnectName,Host, AllNewWebName[i])).start()
    return

def main(web: str):
    port=80
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    Host = findHost(web) #Tim host tu trang web nhap vao
    count = web.count('/') #Dem so / tu trang web de kiem tra request goc
    check = checkIndexFile(web)
    if (count ==2): web = web + '/'
    sock.connect((Host,port))
    send = "GET " + web+ " HTTP/1.1\r\nHost: " + Host + "\r\n\r\n"
    sock.sendall(bytes(send.encode()))
    temp = getHead(sock)
    n = getContentLength(temp.decode())

    if (check == True): # Kiem tra cac request gốc để trả về index.html file
        if (n==-1):
            GetChunkedHTMLData(sock) #Truong hop request goc không có Content Length
        else:
            GetContentLengthHTMLdata(sock,n) #Truong hop request gốc có Content Length
    else: #Cac file khong phai request gốc
        if (n!=-1): #Cac file co content length
            if (web[len(web)-1]=='/'): #Luu cac file trong folder
                getFolderFile(sock,n,web,Host)
            else:
                filename = findFileName(web)
                if filename.find(".")==-1:
                    GetContentLengthHTMLdata(sock,n) #Truong hop cac file khong phai là file folder, khong phai là file co duoi thi se duoc luu vao index.html
                else:
                    GetContentLengthData(sock,n,filename) #Truong hop cac file co content length
        else:
            filename = findFileName(web)
            if (filename.find('.')==-1):
                GetChunkedHTMLData(sock) #Truong hop cac file khong phai la file folder, khong phai la file co duoi se duoc luu vao index.html
            else:
                GetChunkedData(sock,filename) #Truong hop cac file co chunked data
    sock.close()
    return

AllWeb = sys.argv[1:]
for i in AllWeb:
    main(i)
    print("success download file")