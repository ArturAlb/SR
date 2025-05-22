import ssl
import socket
import json
from decrypt_file import decrypt_with_tls_key

HOST = '0.0.0.0'  # Bind to all interfaces
PORT = 443  # Use port 443 for TLS
CERT = "/relay/certs/exit1.crt"
KEY = "/relay/certs/exit1.key"

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
                # Receive the encrypted data (ciphertext)
                ciphertext = ssock.recv(4096)

                if ciphertext:
                    print(f"[+] Received encrypted data ({len(ciphertext)} bytes)")

                    try:
                        # Decrypt the data using the server's private key
                        plaintext = decrypt_with_tls_key(KEY, ciphertext)

                        # Deserialize the JSON data (plaintext should be in JSON format)
                        json_data = json.loads(plaintext.decode('utf-8'))
                        print("[+] Decrypted JSON message:", json_data)

                        # Extract the message from the JSON data
                        message = json_data.get('message')

                        # If 'message' is missing, print an error
                        if not message:
                            print("[!] Missing 'message' in the received data.")
                        else:
                            handle_message(message)

                    except json.JSONDecodeError:
                        print("[!] Error decoding JSON message.")
                    except Exception as e:
                        print("[!] Decryption failed:", str(e))

