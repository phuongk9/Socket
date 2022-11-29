import threading
import socket
from urllib import parse
def firsActivity(URL):
    PORT = 80
    split_url = parse.urlsplit(URL)
    #Get ip 
    HOST = socket.gethostbyname(split_url.netloc)
    client = Client(HOST,PORT,URL)
    client.connect()

def main():
    URL = input("Input url: ")
    manyURL = URL.split()
    numberURL = len(manyURL)
    numberThread = []
    for i in range(0, numberURL):
        numberThread.append(threading.Thread(target=firsActivity, args=(manyURL[i],)))
    for i in numberThread:
        i.start()
    for i in numberThread:
        i.join()

if __name__ == '_main_':
    main()