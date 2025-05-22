import socket
import json

RELAY_IP = '10.1.0.2'   # Replace with actual IP in your network
PORT = 443

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((RELAY_IP, PORT))
    # Mark this as a Tor packet
    message = {
        "is_tor": True,
        "payload": "Hello, relay!"
    }
    json_message = json.dumps(message)
    sock.sendall(json_message.encode())
    data = sock.recv(1024)
    print(f"[+] Relay responded: {data.decode()}")

