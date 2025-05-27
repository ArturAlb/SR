import asyncio
import json
import base64
from cypher_creator import encrypt_with_tls_cert
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCDataChannel
from signaling import post_signal, wait_for_signal


# Load directory info
with open('/volumes/directory.json', 'r') as f:
    directory = json.load(f)
relays = [entry for entry in directory if entry['type'] == 'relay']
exits = [entry for entry in directory if entry['type'] == 'exit']
def write_temp_cert(cert_base64, name):
    cert_path = f"/tmp/{name}.crt"
    with open(cert_path, 'wb') as f:
        f.write(base64.b64decode(cert_base64))
    return cert_path





# Encrypt final message to the exit node
exit_cert =  write_temp_cert(exits[0]['cert_base64'], exits[0]['name'])

inner_msg = "This is the secret message for the final node"
encrypted_inner = encrypt_with_tls_cert(exit_cert, inner_msg.encode('utf-8'))

# Now prepare outer message with next IP and the encrypted payload (as JSON)
middle_msg = {
    "next_ip": "10.1.1.1",
    "message": encrypted_inner
}
json_middle = json.dumps(middle_msg).encode('utf-8')

# Encrypt again for the current relay (hybrid)
obj = next((o for o in relays if o.get('name') == "relay1"), None)

relay_cert = write_temp_cert(obj['cert_base64'], obj['name'])

ciphertext = encrypt_with_tls_cert(relay_cert, json_middle)

# Add 'is_tor' flag to the outermost message
censor_outer = {
    "is_tor": False,
    "payload": ciphertext
}

final_payload = json.dumps(censor_outer).encode('utf-8')

RELAY_KEY = "relay1"
EXIT_KEY = "exit_node1"

async def send_message_via_webrtc():
    pc = RTCPeerConnection()
    channel = pc.createDataChannel("data")

    async def send_on_open():
        await asyncio.sleep(1)
        channel.send(final_payload)
        print("[+] Encrypted onion message sent via WebRTC data channel")
        await asyncio.sleep(7)
        # Keep connection open for more messages. To close, call await pc.close() manually.

    @channel.on("open")
    def on_open():
        asyncio.ensure_future(send_on_open())

    # Create offer and send to signaling server
    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)
    post_signal("relay1", {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type})
    print("[+] Offer sent to signaling server for relay1. Waiting for relay answer...")

    # Wait for relay answer from signaling server
    answer_data = wait_for_signal("client", expected_type="answer")
    answer = RTCSessionDescription(sdp=answer_data['sdp'], type=answer_data['type'])
    await pc.setRemoteDescription(answer)
    print("[+] Got answer from relay. WebRTC channel established.")

    # Wait briefly to ensure message delivery, then close the connection and exit
    await asyncio.sleep(2)
    await pc.close()

if __name__ == "__main__":
    asyncio.run(send_message_via_webrtc())
