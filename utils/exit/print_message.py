import ssl
import socket
import json
from decrypt_file import decrypt_with_tls_key

HOST = '0.0.0.0'  # Bind to all interfaces
PORT = 443  # Use port 443 for TLS
CERT = "certs/exit1.crt"
KEY = "certs/exit1.key"

# Set up SSL context for server
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile=CERT, keyfile=KEY)

# Function to handle the received message
def handle_message(message):
    print(f"[+] Received message: {message}")

# Set up the server to accept connections
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.bind((HOST, PORT))
    sock.listen(5)
    print(f"[+] TLS server listening on port {PORT}...")

    while True:
        # Accept a new connection
        conn, addr = sock.accept()
        with conn:
            print(f"[+] Connection from {addr}")

            # Wrap the connection with SSL context for secure communication
            with context.wrap_socket(conn, server_side=True) as ssock:
                # Receive the encrypted data (as JSON string)
                data = ssock.recv(4096)

                if data:
                    print(f"[+] Received encrypted data ({len(data)} bytes)")

                    try:
                        # Parse the received JSON into a dict
                        enc_dict = json.loads(data.decode('utf-8'))
                        # Decrypt the layer using the server's private key
                        plaintext = decrypt_with_tls_key(KEY, enc_dict)

                        # Try to parse the decrypted plaintext as JSON
                        try:
                            json_data = json.loads(plaintext.decode('utf-8'))
                            print("[+] Decrypted JSON message:", json_data)
                            message = json_data.get('message')
                            if message:
                                handle_message(message)
                            else:
                                print("[!] Missing 'message' in the received data.")
                        except json.JSONDecodeError:
                            # Not JSON, treat as final message
                            print("[+] Final message (not JSON):", plaintext.decode('utf-8', errors='replace'))
                    except Exception as e:
                        print("[!] Decryption failed:", str(e))

