import socket
import ssl

FORWARDER_HOST = '192.168.0.8'
FORWARDER_PORT = 65431

CLIENT_HOST = '192.168.0.6'
CLIENT_PORT = 50

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # allows socket re-use
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # TLS
    s = ssl.wrap_socket(s, keyfile="./privkey.pem", certfile="./certificate.pem")

    # bind the client socket
    s.bind((CLIENT_HOST, CLIENT_PORT))
    
    # connect to the forward socket
    s.connect((FORWARDER_HOST, FORWARDER_PORT))

    print('Connected')

    while True:
        # send data
        print('Sending data')
        s.sendall(b'Hello, world')

        # receive data
        print('Receiving data')
        data = s.recv(1024)

        # echo data
        print('Echoing: ', repr(data))