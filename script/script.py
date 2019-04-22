import socket
import numpy as np

sock = socket.socket()
sock.bind(('', 8080))
sock.listen(1)
conn, addr = sock.accept()
while True:
    data = conn.recv(1000).decode()
    if not data:
        break
    data = data.strip()
    data = [float(x) for x in data.split(' ')]
    inputs = np.asarray(data)
    print(data)
input()
socket.close()