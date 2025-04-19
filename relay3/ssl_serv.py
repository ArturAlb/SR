import ssl
import socket
import json
from decrypt_file import decrypt_with_tls_key  # Assuming this is your decryption function

HOST = '0.0.0.0'  # Bind to all interfaces
PORT = 443  # Use port 443 for TLS
CERT = "certs/relay3.crt"
KEY = "certs/relay3.key"

# Set up SSL context for server
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile=CERT, keyfile=KEY)

# Function to send message to the next relay over TLS
def forward_to_next_relay(next_ip, next_port, message):
    try:
        # Create a secure TLS connection to the next relay
        next_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        
        # Establish the TLS connection with the next relay
        with socket.create_connection((next_ip, next_port)) as sock:
            with next_context.wrap_socket(sock, server_hostname=next_ip) as ssock:
                print(f"[+] Forwarding message to {next_ip}:{next_port} over TLS")
                
                # Send the message (already in plaintext form)
                ssock.sendall(message.encode())
                print("[+] Message forwarded over TLS.")
    except Exception as e:
        print(f"[!] Failed to forward message to {next_ip}: {str(e)}")

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

                            # Extract the next IP and message from the JSON data
                            next_ip = json_data.get('next_ip')
                            message = json_data.get('message')

                            if next_ip and message:
                                # Forward to next relay (as JSON string)
                                forward_to_next_relay(next_ip, 443, json.dumps(message))
                            elif message:
                                print("[+] Final message:", message)
                            else:
                                print("[!] No 'message' field in decrypted JSON.")
                        except json.JSONDecodeError:
                            # Not JSON, treat as final message
                            print("[+] Final message (not JSON):", plaintext.decode('utf-8', errors='replace'))
                    except Exception as e:
                        print("[!] Decryption or forwarding failed:", str(e))
                        message = json_data.get('message')

                        if next_ip and message:
                            # Forward the message to the next relay over TLS
                            forward_to_next_relay(next_ip, PORT, message)
                        else:
                            print("[!] Missing 'next_ip' or 'message' in the received data")

                    except Exception as e:
                        print("[!] Decryption failed:", str(e))

