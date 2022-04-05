from audioop import add
from ipaddress import ip_address, IPv4Address
from pydoc import cli
from queue import Queue
from threading import Thread

import datetime
import os
import socket
import ssl
import time

FORWARDER_HOST = '192.168.0.8'
#FORWARDER_HOST = 'fe80::e1b9:e08a:570:20f7'
# FORWARD_PORT = 65432

CONFIG_FILE = 'config.txt'

TLS_ON = True

# ---------- LOG FILE ----------
date_now = datetime.datetime.fromtimestamp(time.time())
date_now = str(date_now).replace(":", "_", 3).replace(".", "_", 1).replace(" ", "_", 1)

def logData(queue):
    if not os.path.isdir("forwarder_logs"):
        os.mkdir("forwarder_logs")

    logFile = open("forwarder_logs/forwarder_log" + date_now + ".txt", "w")
    logFile.flush()

    while True:
        info = queue.get()

        if info == "kill":
            break

        logFile.write(info)
        logFile.flush()
    logFile.close()
  
    return

dataQueue = Queue()
logDataThread = Thread(target=logData, args=(dataQueue,))
logDataThread.start()
# ------------------------------

# ---------- RECEIVE ALL ----------
# helper function to receive n bytes or return None if EOF is reached
# def recvall(sock, n):
#     data = bytearray()

#     while len(data) < n:
#         packet = sock.recv(n - len(data))
#         if not packet:
#             return None
#         data.extend(packet)
#     return data
# ------------------------------

# ---------- CONFIG FILE ----------
# read and convert config file
def readConfig(file: str):
    data = open(file).readlines()

    pairs = []

    for line in data:
        myList = line.strip().split(";")

        # forwarder port
        forwardPort = int(myList[0])
        
        # target address (IP + Port)
        targetAddress = myList[1].split(" ")

        targetIP = targetAddress[0]
        targetPort = int(targetAddress[1])
      
        # target address: Convert to tuple
        targetTuple = (targetIP, targetPort)

        # convert to dictionary
        pairs.append([forwardPort, targetTuple])
    
    print(pairs)

    return pairs
# ------------------------------

# ---------- ECHO ----------
def handleWrite(r, w):
    while True:
        data = r.recv(4096)
        w.sendall(data)
# ------------------------------

def handlePortForwarder(s: socket, serverOpts):
    serverAddress, serverPort = serverOpts
    s.listen()
	
    while True: 
        clientConn, clientAddr = s.accept()
 
        # check if serverOpts address is Ipv?/Invalid
        if validIPAddress(FORWARDER_HOST) == "IPv4":
            clientAddress, clientPort = clientAddr
            serverConn, serverAddr = createServerSocket(serverOpts, True)
            serverAddress, serverPort = serverAddr
        else:
            clientAddress, clientPort, temp, level = clientAddr
            serverConn, serverAddr = createServerSocket(serverOpts, False)
            serverAddress, serverPort, temp, level = serverAddr

        log = "Client [" + clientAddress + ":" + str(clientPort) + "] connected to Server [" + serverAddress + ":" + str(serverPort) + "]\n"
        dataQueue.put(log)

        Thread(target=handleWrite, args=(clientConn, serverConn,)).start()
        Thread(target=handleWrite, args=(serverConn, clientConn,)).start()

# ---------- CREATE FORWARDER SOCKET ----------
def createSocket(host, port, ipv4):
    forwarder = None

    if ipv4:
        # create IPv4 Socket
        forwarder = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        forwarder.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # TLS
        forwarder = ssl.wrap_socket(
            forwarder, server_side=True, keyfile="privkey.pem", certfile="certificate.pem"
        )

        forwarder.bind((host, port))
    else: 
        # create IPv6 socket
        forwarder = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        forwarder.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # TLS
        forwarder = ssl.wrap_socket(
            forwarder, server_side=True, keyfile="privkey.pem", certfile="certificate.pem"
        )

        forwarder.bind((host, port, 0, 3))

    return forwarder
# ------------------------------

# ---------- CREATE SERVER SOCKET ----------
def createServerSocket(target, ipv4):
    server = None
    
    if ipv4:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.connect(target)
    else:
        server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.connect((target[0], target[1], 0, 3))
        
    return server, server.getpeername()
# ------------------------------

# ---------- IPv4 or IPv6 ----------
def validIPAddress(IP: str) -> str:
    try:
        return "IPv4" if type(ip_address(IP)) is IPv4Address else "IPv6"
    except ValueError:
        return "Invalid"
# ------------------------------

def main():
    print ('Starting program...')

    # load config file
    portConfig = readConfig(CONFIG_FILE)

    for pair in portConfig:
        forwarderPort = pair[0]
        
        if validIPAddress(FORWARDER_HOST) == "IPv4":
            s = createSocket(FORWARDER_HOST, forwarderPort, True)
        else:
            s = createSocket(FORWARDER_HOST, forwarderPort, False)
        
        # create thread
        Thread(target=handlePortForwarder, args=(s, pair[1],)).start()

if __name__ == "__main__":
    main()
