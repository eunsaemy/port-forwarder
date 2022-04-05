import socket
import ssl

# FORWARDER_HOST = '192.168.0.8'
FORWARDER_HOST = 'fe80::e1b9:e08a:570:20f7'
FORWARDER_PORT = 65433

# CLIENT_HOST = '192.168.0.7'
CLIENT_HOST = 'fe80::eac0:274b:2427:946d'
CLIENT_PORT = 50

with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
    # allows socket re-use
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # TLS
    s = ssl.wrap_socket(s, keyfile="./privkey.pem", certfile="./certificate.pem")

    # bind the client socket
    s.bind((CLIENT_HOST, CLIENT_PORT, 0, 3))
    
    # connect to the forward socket
    s.connect((FORWARDER_HOST, FORWARDER_PORT, 0, 3))

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
