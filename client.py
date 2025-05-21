# client.py
import asyncio
import json
import ssl
from aiohttp import ClientSession
from aiortc import RTCPeerConnection, RTCSessionDescription

async def run_client():
    print("🔧 Creating RTCPeerConnection")
    pc = RTCPeerConnection()
    channel = pc.createDataChannel("chat")

    @channel.on("open")
    def on_open():
        print("📡 Data channel opened — sending message to proxy")
        channel.send("Hello from client!")

    @channel.on("message")
    def on_message(message):
        print(f"📩 Received from proxy: {message}")

    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)
    print("📝 Created offer and set local description")

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with ClientSession() as session:
        print("📬 Sending offer to signaling server")
        await session.post("https://localhost:8443/offer", json={
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        }, ssl=ssl_context)

        print("⏳ Waiting for answer from proxy...")
        while True:
            async with session.get("https://localhost:8443/answer", ssl=ssl_context) as resp:
                if resp.status == 200:
                    answer_json = await resp.json()
                    print("✅ Got answer from proxy")
                    break
                await asyncio.sleep(1)

        answer = RTCSessionDescription(sdp=answer_json["sdp"], type=answer_json["type"])
        await pc.setRemoteDescription(answer)
        print("🔐 Set remote description")

        await asyncio.sleep(10)
        print("🧹 Closing connection")
        await pc.close()

if __name__ == "__main__":
    asyncio.run(run_client())

