import asyncio
import json
from decrypt_file import decrypt_with_tls_key
from aiortc import RTCPeerConnection, RTCSessionDescription
from signaling import post_signal, wait_for_signal
import sys
import os

def log(msg):
    print(f"[RELAY] {msg}", file=sys.stderr)

RELAY_ID = os.getenv("RELAY_ID", "relay1")
KEY = f"relay/certs/{RELAY_ID}.key"

async def relay_server():
    pc = RTCPeerConnection()
    received_data = None

    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        def on_message(message):
            nonlocal received_data
            log("Relay received message via WebRTC")
            received_data = message
            asyncio.ensure_future(handle_and_forward(message))

    # Wait for offer from client via signaling server
    log("Relay waiting for offer via signaling server...")
    offer_data = None
    while offer_data is None:
        log(f"No offer received for {RELAY_ID}. Waiting...")
        await asyncio.sleep(2)
        offer_data = wait_for_signal(RELAY_ID, expected_type="offer")
    offer = RTCSessionDescription(sdp=offer_data['sdp'], type=offer_data['type'])
    await pc.setRemoteDescription(offer)

    # Create answer and send to signaling server
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    post_signal("client", {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type})
    log("Relay1 sent answer to signaling server.")

    # Wait for message to be received and processed
    while received_data is None:
        await asyncio.sleep(1)
    await asyncio.sleep(3)
    await pc.close()

async def handle_and_forward(message):
    # Decrypt current layer
    try:
        enc_dict = json.loads(message.decode('utf-8'))
        if "payload" in enc_dict:
            enc_dict = enc_dict["payload"]
        plaintext = decrypt_with_tls_key(KEY, enc_dict)
        # Try to parse as JSON for next hop
        json_data = json.loads(plaintext.decode('utf-8'))
        next_ip = json_data.get('next_ip')
        next_message = json_data.get('message')
        if next_ip and next_message:
            log(f"Forwarding to next hop {next_ip} via WebRTC")
            await forward_to_next_relay(next_message)
    except Exception as e:
        log(f"Error processing/forwarding: {e}")

async def forward_to_next_relay(message):
    pc = RTCPeerConnection()
    channel = pc.createDataChannel("data")
    log("[RELAY] Data channel created for next hop")

    async def send_on_open():
        log("[RELAY] Data channel open, sending message...")
        await asyncio.sleep(1)
        channel.send(json.dumps(message).encode('utf-8'))
        log("[RELAY] Forwarded message to next hop via WebRTC")
        await asyncio.sleep(2)
        await pc.close()

    @channel.on("open")
    def on_open():
        log("[RELAY] Data channel open event triggered")
        asyncio.ensure_future(send_on_open())

    # Determine the next exit node's signaling key based on next_ip or message context
    import os
    next_ip = message.get("next_ip")
    # Simple mapping: e.g., 10.1.1.1 -> exit1, 10.1.1.2 -> exit2, etc.
    ip_to_exit_id = {
        "10.1.1.1": "exit1",
        "10.1.1.2": "exit2",
        "10.1.1.3": "exit3"
    }
    exit_id = ip_to_exit_id.get(next_ip, "exit1")

    # Create offer and send to signaling server for the correct exit node
    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)
    post_signal(exit_id, {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type})
    print(f"[RELAY] Sent offer for {exit_id} node. Waiting for answer...")

    # Wait for answer from the correct exit node
    while True:
        answer_data = wait_for_signal("relay1", expected_type="answer")
        if answer_data:
            answer = RTCSessionDescription(sdp=answer_data['sdp'], type=answer_data['type'])
            await pc.setRemoteDescription(answer)
            print(f"[RELAY] Got answer from {exit_id} node.")
            break
        await asyncio.sleep(1)
    await asyncio.sleep(3)
    await pc.close()

if __name__ == "__main__":
    import asyncio
    async def main():
        while True:
            await relay_server()
    asyncio.run(main())

