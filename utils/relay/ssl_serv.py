import ssl
import socket
import json
from decrypt_file import decrypt_with_tls_key  # Your decryption function

HOST = '0.0.0.0'
PORT = 443
CERT = "/volumes/certs/cert.crt"
KEY = "/volumes/certs/cert.key"

# Server SSL context (for incoming TLS connections)
server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
server_context.load_cert_chain(certfile=CERT, keyfile=KEY)
server_context.check_hostname = False
server_context.verify_mode = ssl.CERT_NONE

# Client SSL context (used to forward to next relay over TLS)
client_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
client_context.check_hostname = False
client_context.verify_mode = ssl.CERT_NONE

def forward_to_next_relay(next_ip, next_port, message):
    try:
        with socket.create_connection((next_ip, next_port)) as sock:
            with client_context.wrap_socket(sock, server_hostname=next_ip) as ssock:
                print(f"[+] Forwarding message to {next_ip}:{next_port} over TLS")
                ssock.sendall(message.encode())
                ssock.shutdown(socket.SHUT_WR)
                print("[+] Message forwarded and connection closed.")
    except Exception as e:
        print(f"[!] Failed to forward message to {next_ip}: {e}")

def recv_all(sock):
    buffer = b''
    while True:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                break
            buffer += chunk
        except Exception as e:
            print(f"[!] Error receiving data: {e}")
            break
    return buffer

# Main server loop
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
    listener.bind((HOST, PORT))
    listener.listen(5)
    print(f"[+] Relay listening on {HOST}:{PORT}...")

    while True:
        conn, addr = listener.accept()
        print(f"[+] Incoming connection from {addr}")

        try:
            # Peek at first byte without consuming it to detect TLS
            first_byte = conn.recv(1, socket.MSG_PEEK)
            is_tls = first_byte and first_byte[0] == 0x16

            if is_tls:
                print("[+] Detected TLS connection")
                try:
                    with server_context.wrap_socket(conn, server_side=True) as tls_conn:
                        data = recv_all(tls_conn)
                except ssl.SSLError as e:
                    print(f"[!] TLS handshake failed: {e}")
                    conn.close()
                    continue
            else:
                print("[+] Detected plain TCP connection")
                data = recv_all(conn)
                conn.close()

            if not data:
                print("[!] No data received; skipping.")
                continue

            try:
                enc_dict = json.loads(data.decode('utf-8'))
                if "payload" in enc_dict:
                    enc_dict = enc_dict["payload"]

                plaintext = decrypt_with_tls_key(KEY, enc_dict)
            except Exception as e:
                print(f"[!] Error decrypting or parsing data: {e}")
                continue

            try:
                json_data = json.loads(plaintext.decode('utf-8'))
                print("[+] Decrypted JSON message:", json_data)

                next_ip = json_data.get('next_ip')
                message = json_data.get('message')

                if next_ip and message:
                    forward_to_next_relay(next_ip, 443, json.dumps(message))
                elif message:
                    print(f"[+] Final message: {message}")
            except Exception as e:
                print(f"[!] Error parsing decrypted plaintext as JSON: {e}")

        except Exception as e:
            print(f"[!] General error handling connection from {addr}: {e}")

