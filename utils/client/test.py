import ssl
import socket
import json
import base64
from cypher_creator import encrypt_with_tls_cert

relay_ip = '10.1.0.2'
relay_port = 443

# Encrypt final message to the exit node
exit_cert = 'certs/exit1.crt'
inner_msg = "This is the secret message for the final node"
# Hybrid encrypt for exit node
encrypted_inner = encrypt_with_tls_cert(exit_cert, inner_msg.encode('utf-8'))

# Now prepare outer message with next IP and the encrypted payload (as JSON)
middle_msg = {
    "next_ip": "10.1.1.1",  # this is where the next relay should forward
    "message": encrypted_inner  # This is a dict
}
json_middle = json.dumps(middle_msg).encode('utf-8')

# Encrypt again for the current relay (hybrid)
relay_cert = 'certs/relay1.crt'
ciphertext = encrypt_with_tls_cert(relay_cert, json_middle)
# ciphertext is a dict (enc_key, iv, ciphertext)

# Serialize final payload to send (as JSON)
final_payload = json.dumps(ciphertext).encode('utf-8')

# Send it
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

with socket.create_connection((relay_ip, relay_port)) as sock:
    with context.wrap_socket(sock, server_hostname=relay_ip) as ssock:
        ssock.sendall(json.dumps(ciphertext).encode('utf-8'))
        print("[+] Encrypted onion message sent")

