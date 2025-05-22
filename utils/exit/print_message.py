import asyncio
import json
from decrypt_file import decrypt_with_tls_key
from aiortc import RTCPeerConnection, RTCSessionDescription
from signaling import post_signal, wait_for_signal
import sys
KEY = "relay/certs/exit1.key"

def log(msg):
    print(f"[EXIT] {msg}", file=sys.stderr)

async def exit_server():
    pc = RTCPeerConnection()
    received_data = None

    @pc.on("datachannel")
    def on_datachannel(channel):
        log("[EXIT] Data channel created")
        @channel.on("open")
        def on_open():
            log("[EXIT] Data channel open event triggered")
        @channel.on("message")
        def on_message(message):
            log(f"[EXIT] on_message called with: {repr(message)}")
            nonlocal received_data
            log("Exit node received message via WebRTC")
            received_data = message
            asyncio.ensure_future(handle_message(message))

    # Wait for offer from relay via signaling server
    import os
    EXIT_ID = os.environ.get("EXIT_ID", "exit1")
    print(f"[EXIT] Waiting for offer via signaling key: {EXIT_ID}", file=sys.stderr)
    offer_data = None
    while offer_data is None:
        await asyncio.sleep(2)
        offer_data = wait_for_signal(EXIT_ID, expected_type="offer")
    # Register datachannel handler BEFORE setting remote description
    @pc.on("datachannel")
    def on_datachannel(channel):
        log("[EXIT] Data channel created")
        @channel.on("open")
        def on_open():
            log("[EXIT] Data channel open event triggered")
        @channel.on("message")
        def on_message(message):
            log(f"[EXIT] on_message called with: {repr(message)}")
            nonlocal received_data
            log("Exit node received message via WebRTC")
            received_data = message
            asyncio.ensure_future(handle_message(message))

    offer = RTCSessionDescription(sdp=offer_data['sdp'], type=offer_data['type'])
    await pc.setRemoteDescription(offer)
    log("[EXIT] Remote description set for offer")

    # Create answer and send to signaling server
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    post_signal("relay1", {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type})
    print(f"[EXIT] Answer sent to relay1", file=sys.stderr)

    # Wait for message to be received and processed
    while received_data is None:
        await asyncio.sleep(1)
    # Keep connection open for more messages. To close, call await pc.close() manually.
    while True:
        await asyncio.sleep(10)
        # Optionally, add logic to process more messages

async def handle_message(message):
    try:
        enc_dict = json.loads(message.decode('utf-8'))
        plaintext = decrypt_with_tls_key(KEY, enc_dict)
        try:
            json_data = json.loads(plaintext.decode('utf-8'))
            msg = json_data.get('message')
            if msg:
                print(f"[EXIT] Final message: {msg}", file=sys.stderr)
        except json.JSONDecodeError:
            log(f"Final message (not JSON): {plaintext.decode('utf-8', errors='replace')}")
    except Exception as e:
        log(f"Decryption failed: {e}")

if __name__ == "__main__":
    import asyncio
    async def main():
        while True:
            await exit_server()
    asyncio.run(main())
