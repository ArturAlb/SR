import socket
import json
import random
import base64
from cypher_creator import encrypt_with_tls_cert

from time import sleep

# Load directory info
with open('/volumes/directory.json', 'r') as f:
    directory = json.load(f)

# Separate nodes by type
relays = [entry for entry in directory if entry['type'] == 'relay-tor']
exits = [entry for entry in directory if entry['type'] == 'exit']

if len(relays) < 2 or len(exits) == 0:
    raise ValueError("Need at least 2 relays and 1 exit node")

# Randomly pick 2 relays and 1 exit node
# entry_relay, middle_relay = random.sample(relays, 2)



# Show menu to select entry relay
print("┌─────────────────────────────────────────────┐")
print("│ [*] Available entry relays                  │")
print("┌─────────────────────────────────────────────┐")
for i, relay in enumerate(relays):
    line = f"{i}) {relay['name']} ({relay['ip']})"
    print(f"│ {line:<44}│")
print("└─────────────────────────────────────────────┘")


# User selects one
while True:
    try:
        choice = int(input("Select an entry relay by index: "))
        if 0 <= choice < len(relays):
            entry_relay = relays.pop(choice)  # Remove chosen relay from list
            break
        else:
            print("Invalid index. Try again.")
    except ValueError:
        print("Please enter a valid number.")

# Pick a random middle relay from remaining relays
num = random.randint(0, len(relays) -1)
middle_relay = relays[num]
print("Middle relay: ", middle_relay['name'])
exit_node = random.choice(exits)

print(f"[+] Chosen path:\n  Entry: {entry_relay['name']} ({entry_relay['ip']})\n  Middle: {middle_relay['name']} ({middle_relay['ip']})\n  Exit: {exit_node['name']} ({exit_node['ip']})")

# Decode certs from base64 to PEM format
def write_temp_cert(cert_base64, name):
    cert_path = f"/tmp/{name}.crt"
    with open(cert_path, 'wb') as f:
        f.write(base64.b64decode(cert_base64))
    return cert_path

exit_cert_path = write_temp_cert(exit_node['cert_base64'], exit_node['name'])
middle_cert_path = write_temp_cert(middle_relay['cert_base64'], middle_relay['name'])
entry_cert_path = write_temp_cert(entry_relay['cert_base64'], entry_relay['name'])

# Encrypt final message to the exit node
exit_msg = "This is the secret message for the final node"
encrypted_exit = encrypt_with_tls_cert(exit_cert_path, exit_msg.encode('utf-8'))

# Wrap in middle relay layer
middle_msg = {
    "next_ip": exit_node['ip'],
    "message": encrypted_exit
}
encrypted_middle = encrypt_with_tls_cert(middle_cert_path, json.dumps(middle_msg).encode('utf-8'))

# Wrap in entry relay layer
entry_msg = {
    "next_ip": middle_relay['ip'],
    "message": encrypted_middle
}
encrypted_entry = encrypt_with_tls_cert(entry_cert_path, json.dumps(entry_msg).encode('utf-8'))

# Final payload sent over TCP 
outermost = {
    "is_tor": True,
    "payload": encrypted_entry
}
final_payload = json.dumps(outermost).encode('utf-8')



# Connect using plain TCP (no TLS)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((entry_relay['ip'], 443))
    print(f"[+] Connected to entry relay at {entry_relay['ip']}:443 over plain TCP")
    
    try:
            sock.sendall(final_payload)
            print("[+] Encrypted onion message sent to entry relay over plain TCP")
            sleep(2)  # Wait 2 seconds before sending the next message
    except KeyboardInterrupt:
        print("[*] Stopped sending messages.")
    finally:
        sock.shutdown(socket.SHUT_WR)

