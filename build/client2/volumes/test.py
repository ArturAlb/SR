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

# Add 'is_tor' flag to the outermost message
censor_outer = {
    "is_tor": False,
    "payload": ciphertext
}

# Serialize final payload to send (as JSON)
final_payload = json.dumps(censor_outer).encode('utf-8')

# Send it over plain TCP (no TLS) so the censor can see the is_tor flag
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((relay_ip, relay_port))
    sock.sendall(final_payload)
    print("[+] Encrypted onion message sent (with plaintext is_tor flag over TCP)")

