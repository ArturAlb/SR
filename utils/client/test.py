import asyncio
import json
import base64
from cypher_creator import encrypt_with_tls_cert
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCDataChannel
from signaling import post_signal, wait_for_signal

# Encrypt final message to the exit node
exit_cert = 'certs/exit1.crt'
inner_msg = "This is the secret message for the final node"
encrypted_inner = encrypt_with_tls_cert(exit_cert, inner_msg.encode('utf-8'))

# Now prepare outer message with next IP and the encrypted payload (as JSON)
middle_msg = {
    "next_ip": "10.1.1.1",
    "message": encrypted_inner
}
json_middle = json.dumps(middle_msg).encode('utf-8')

# Encrypt again for the current relay (hybrid)
relay_cert = 'certs/relay1.crt'
ciphertext = encrypt_with_tls_cert(relay_cert, json_middle)

# Add 'is_tor' flag to the outermost message
censor_outer = {
    "is_tor": True,
    "payload": ciphertext
}

final_payload = json.dumps(censor_outer).encode('utf-8')

RELAY_KEY = "relay1"
EXIT_KEY = "exit1"

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
