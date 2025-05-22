import socket
import threading
import json
import os

# Configuration
LISTEN_HOST = '0.0.0.0'  # Listen on all interfaces
LISTEN_PORT = 8080        # This must match your iptables REDIRECT port
RELAY_HOST = '10.1.0.2'  # Change to your relay's IP if different
RELAY_PORT = 443

BUFFER_SIZE = 4096

def is_tor_message(data):
    try:
        msg = json.loads(data.decode('utf-8'))
        return msg.get('is_tor', False)
    except Exception:
        return False

def handle_client(client_sock, client_addr):
    print(f"[+] Connection from {client_addr}")
    try:
        # Receive the initial data from the client
        data = client_sock.recv(BUFFER_SIZE)
        if not data:
            client_sock.close()
            return
        print(f"[LOG] Received {len(data)} bytes from client")
        # Check for Tor flag
        if is_tor_message(data):
            print("[ALERT] Tor message detected! Blocking connection.")
            client_sock.close()
            return
        # Forward to relay
        with socket.create_connection((RELAY_HOST, RELAY_PORT)) as relay_sock:
            relay_sock.sendall(data)
            # Start bidirectional forwarding
            t1 = threading.Thread(target=pipe, args=(client_sock, relay_sock))
            t2 = threading.Thread(target=pipe, args=(relay_sock, client_sock))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
    except Exception as e:
        print(f"[!] Error handling client: {e}")
    finally:
        client_sock.close()

def pipe(src, dst):
    try:
        while True:
            data = src.recv(BUFFER_SIZE)
            if not data:
                break
            dst.sendall(data)
    except Exception:
        pass
    finally:
        src.close()
        dst.close()

def start_proxy():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((LISTEN_HOST, LISTEN_PORT))
        server_sock.listen(100)
        print(f"[+] TCP Proxy Censor listening on {LISTEN_HOST}:{LISTEN_PORT}")
        while True:
            client_sock, client_addr = server_sock.accept()
            threading.Thread(target=handle_client, args=(client_sock, client_addr), daemon=True).start()

if __name__ == "__main__":
    # Add iptables REDIRECT rule for TCP port 443 to redirect to proxy port 8080
    try:
        os.system(f"iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to-port {LISTEN_PORT}")
        print(f"[+] iptables REDIRECT rule added: TCP 443 -> {LISTEN_PORT}")
    except Exception as e:
        print(f"[!] Failed to add iptables REDIRECT rule: {e}")
    start_proxy()
