# https_signaling_server.py
import asyncio
from aiohttp import web
import ssl

offer_data = None
answer_data = None

async def post_offer(request):
    global offer_data, answer_data
    offer_data = await request.json()
    answer_data = None  # Reset any previous answer
    print("✅ Received offer from client")
    return web.Response(text="Offer received")

async def get_offer(request):
    global offer_data
    if offer_data:
        print("📤 Sending offer to proxy")
        return web.json_response(offer_data)
    return web.Response(status=204)

async def post_answer(request):
    global answer_data
    answer_data = await request.json()
    print("✅ Received answer from proxy")
    return web.Response(text="Answer received")

async def get_answer(request):
    global answer_data
    if answer_data:
        print("📤 Sending answer to client")
        return web.json_response(answer_data)
    return web.Response(status=204)

app = web.Application()
app.add_routes([
    web.post("/offer", post_offer),
    web.get("/offer", get_offer),
    web.post("/answer", post_answer),
    web.get("/answer", get_answer)
])

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain("cert.pem", "key.pem")

print("🚀 HTTPS signaling server starting at https://localhost:8443")
web.run_app(app, port=8443, ssl_context=ssl_context)

