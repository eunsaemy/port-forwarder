import socket
from threading import Thread

# SERVER_HOST = '192.168.0.9'
SERVER_HOST = 'fe80::5ef5:9aac:1a79:5e9e'
SERVER_PORT = 7000

def handleWrite(r, w):
    while True:
        # data = recvall(r, 4096)
        
        # receive data
        data = r.recv(4096).decode()
        data = 'From port ' + str(SERVER_PORT) + ': ' + data

        # send response
        w.sendall(data.encode())

with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
    # allows socket re-use
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # bind the server socket
    s.bind((SERVER_HOST, SERVER_PORT, 0, 3))

    # listen on the specified host + port
    s.listen()

    while True:
        conn, addr = s.accept()
        print('Client connected')

        # create thread
        Thread(target=handleWrite, args=(conn, conn,)).start()
