import ssl
import socket
import json
from decrypt_file import decrypt_with_tls_key  # Your decryption function

HOST = '0.0.0.0'
PORT = 443
CERT = "/volumes/certs/cert.crt"
KEY = "/volumes/certs/cert.key"

# Server SSL context (for incoming connections)
server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
server_context.load_cert_chain(certfile=CERT, keyfile=KEY)

# Disable verification because of self signed certs
server_context.check_hostname = False
server_context.verify_mode = ssl.CERT_NONE

# Client SSL context (for forwarding to next relay)
client_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)

# Disable verification because of self signed certs
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

def recv_all_tls(sock):
    # TLS socket recv: same as regular, but you need to handle partial reads
    buffer = b''
    while True:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                break
            buffer += chunk
        except ssl.SSLWantReadError:
            continue
        except Exception as e:
            print(f"[!] Error receiving data: {e}")
            break
    return buffer

# Main server loop
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.bind((HOST, PORT))
    sock.listen(5)
    print(f"[+] TLS server listening on {HOST}:{PORT}...")

    while True:
        conn, addr = sock.accept()
        print(f"[+] Incoming connection from {addr}")
        try:
            with server_context.wrap_socket(conn, server_side=True) as tls_conn:
                print(f"[+] TLS handshake completed with {addr}")

                data = recv_all_tls(tls_conn)
                if not data:
                    print("[!] No data received; closing connection.")
                    continue

                print(f"[+] Received data ({len(data)} bytes)")

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

        except ssl.SSLError as ssl_err:
            print(f"[!] TLS error with connection from {addr}: {ssl_err}")
        except Exception as ex:
            print(f"[!] General error handling connection from {addr}: {ex}")

