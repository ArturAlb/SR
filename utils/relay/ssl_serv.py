import sys
import os
import json
import ssl
import socket
import threading
import asyncio
import base64
from decrypt_file import decrypt_with_tls_key  # Your decryption function

# For WebRTC
try:
    from aiortc import RTCPeerConnection, RTCSessionDescription
    from signaling import post_signal, wait_for_signal
except ImportError:
    # Not required for TOR mode
    pass


# --- TOR Mode ---

HOST = '0.0.0.0'
PORT = 443
CERT = "/volumes/certs/cert.crt"
KEY = "/volumes/certs/cert.key"

server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
server_context.load_cert_chain(certfile=CERT, keyfile=KEY)
server_context.check_hostname = False
server_context.verify_mode = ssl.CERT_NONE

client_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
client_context.check_hostname = False
client_context.verify_mode = ssl.CERT_NONE

def forward_to_next_relay_tls(next_ip, next_port, message):
    try:
        with socket.create_connection((next_ip, next_port)) as sock:
            with client_context.wrap_socket(sock, server_hostname=next_ip) as ssock:
                print(f"[+] Forwarding message to {next_ip}:{next_port} over TLS")
                ssock.sendall(message.encode())
                ssock.shutdown(socket.SHUT_WR)
                print("[+] Message forwarded and connection closed.")
    except Exception as e:
        print(f"[!] Failed to forward message to {next_ip}: {e}")

def recv_all(sock):
    buffer = b''
    while True:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                break
            buffer += chunk
        except Exception as e:
            print(f"[!] Error receiving data: {e}")
            break
    return buffer

def handle_connection(conn, addr):
    print(f"[+] Incoming connection from {addr}")
    try:
        first_byte = conn.recv(1, socket.MSG_PEEK)
        is_tls = first_byte and first_byte[0] == 0x16

        if is_tls:
            print("[+] Detected TLS connection")
            try:
                with server_context.wrap_socket(conn, server_side=True) as tls_conn:
                    data = recv_all(tls_conn)
            except ssl.SSLError as e:
                print(f"[!] TLS handshake failed: {e}")
                conn.close()
                return
        else:
            print("[+] Detected plain TCP connection")
            data = recv_all(conn)
            conn.close()

        if not data:
            print("[!] No data received; skipping.")
            return

        try:
            enc_dict = json.loads(data.decode('utf-8'))
            if "payload" in enc_dict:
                enc_dict = enc_dict["payload"]

            plaintext = decrypt_with_tls_key(KEY, enc_dict)
        except Exception as e:
            print(f"[!] Error decrypting or parsing data: {e}")
            return

        try:
            json_data = json.loads(plaintext.decode('utf-8'))
            print("[+] Decrypted JSON message:", json_data)

            next_ip = json_data.get('next_ip')
            message = json_data.get('message')

            if next_ip and message:
                forward_to_next_relay_tls(next_ip, 443, json.dumps(message))
            elif message:
                print(f"[+] Final message: {message}")
        except Exception as e:
            print(f"[!] Error parsing decrypted plaintext as JSON: {e}")
    except Exception as e:
        print(f"[!] General error handling connection from {addr}: {e}")

def run_tor_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind((HOST, PORT))
        listener.listen(5)
        print(f"[+] Relay listening on {HOST}:{PORT} (TOR mode)...")

        while True:
            conn, addr = listener.accept()
            threading.Thread(target=handle_connection, args=(conn, addr), daemon=True).start()


# --- WebRTC Mode ---

def write_temp_cert(cert_base64, name):
    cert_path = f"/tmp/{name}.crt"
    with open(cert_path, 'wb') as f:
        f.write(base64.b64decode(cert_base64))
    return cert_path


""" with open('/volumes/directory.json', 'r') as f:
    directory = json.load(f)
relays = [entry for entry in directory if entry['type'] == 'relay']
print(relays)
RELAY_ID = os.getenv("RELAY_ID", "relay1")
print(RELAY_ID)
obj = next((o for o in relays if o.get('name') == RELAY_ID), None)
KEY_WEBRTC = write_temp_cert(obj['cert_base64'], obj['name']) """

RELAY_ID = os.getenv("RELAY_ID", "relay1")
KEY_WEBRTC = f"/volumes/certs/cert.key"

def log(msg):
    print(f"[RELAY] {msg}", file=sys.stderr)

async def handle_and_forward_webrtc(message):
    try:
        enc_dict = json.loads(message.decode('utf-8'))
        if "payload" in enc_dict:
            enc_dict = enc_dict["payload"]
        plaintext = decrypt_with_tls_key(KEY_WEBRTC, enc_dict)
        json_data = json.loads(plaintext.decode('utf-8'))
        next_ip = json_data.get('next_ip')
        next_message = json_data.get('message')
        if next_ip and next_message:
            log(f"Forwarding to next hop {next_ip} via WebRTC")
            await forward_to_next_relay_webrtc(next_ip, next_message)
    except Exception as e:
        log(f"Error processing/forwarding: {e}")

async def forward_to_next_relay_webrtc(next_ip, message):
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

    ip_to_exit_id = {
        "10.1.1.1": "exit_node1",
        "10.1.1.2": "exit_node2",
        "10.1.1.3": "exit_node3"
    }
    exit_id = ip_to_exit_id.get(next_ip, "exit_node1")

    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)
    post_signal(exit_id, {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type})
    log(f"[RELAY] Sent offer for {exit_id} node. Waiting for answer...")

    while True:
        answer_data = wait_for_signal(RELAY_ID, expected_type="answer")
        if answer_data:
            answer = RTCSessionDescription(sdp=answer_data['sdp'], type=answer_data['type'])
            await pc.setRemoteDescription(answer)
            log(f"[RELAY] Got answer from {exit_id} node.")
            break
        await asyncio.sleep(1)
    await asyncio.sleep(3)
    await pc.close()

async def relay_server_webrtc():
    pc = RTCPeerConnection()
    received_data = None

    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        def on_message(message):
            nonlocal received_data
            log("Relay received message via WebRTC")
            received_data = message
            asyncio.ensure_future(handle_and_forward_webrtc(message))

    log("Relay waiting for offer via signaling server...")
    offer_data = None
    while offer_data is None:
        log(f"No offer received for {RELAY_ID}. Waiting...")
        await asyncio.sleep(2)
        offer_data = wait_for_signal(RELAY_ID, expected_type="offer")

    offer = RTCSessionDescription(sdp=offer_data['sdp'], type=offer_data['type'])
    await pc.setRemoteDescription(offer)

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    post_signal("client", {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type})
    log("Relay sent answer to signaling server.")

    while received_data is None:
        await asyncio.sleep(1)
    await asyncio.sleep(3)
    await pc.close()

async def run_webrtc_server():
    while True:
        await relay_server_webrtc()


# --- Main entry point ---

def print_usage():
    print("Usage: python relay.py --mode [tor|webrtc]")
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] != '--mode':
        print_usage()

    mode = sys.argv[2].lower()
    if mode == "tor":
        run_tor_server()
    elif mode == "webrtc":
        asyncio.run(run_webrtc_server())
    else:
        print(f"Unknown mode: {mode}")
        print_usage()
