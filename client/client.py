import socket

RELAY_IP = '10.1.0.2'   # Replace with actual IP in your network
PORT = 443

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((RELAY_IP, PORT))
    message = "Hello, relay!"
    sock.sendall(message.encode())
    data = sock.recv(1024)
    print(f"[+] Relay responded: {data.decode()}")

