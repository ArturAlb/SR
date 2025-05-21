# proxy.py
import asyncio
import json
import ssl
from aiohttp import ClientSession
from aiortc import RTCPeerConnection, RTCSessionDescription

async def run_proxy():
    print("🔧 Creating RTCPeerConnection")
    pc = RTCPeerConnection()

    @pc.on("datachannel")
    def on_datachannel(channel):
        print(f"📡 Received data channel: {channel.label}")

        @channel.on("message")
        def on_message(message):
            print(f"📩 Received from client: {message}")
            print("📤 Sending response to client...")
            channel.send("Hello from proxy!")

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with ClientSession() as session:
        print("⏳ Polling signaling server for offer...")
        while True:
            async with session.get("https://localhost:8443/offer", ssl=ssl_context) as resp:
                if resp.status == 200:
                    offer_json = await resp.json()
                    print("✅ Got offer from client")
                    break
                await asyncio.sleep(1)

        offer = RTCSessionDescription(sdp=offer_json["sdp"], type=offer_json["type"])
        await pc.setRemoteDescription(offer)
        print("🔐 Set remote description")

        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        print("📝 Created answer and set local description")

        print("📬 Sending answer to signaling server")
        await session.post("https://localhost:8443/answer", json={
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        }, ssl=ssl_context)

        await asyncio.sleep(10)
        print("🧹 Closing connection")
        await pc.close()

if __name__ == "__main__":
    asyncio.run(run_proxy())

