from scapy.all import sniff, send, IP, TCP, Raw, get_if_list
import json

INTERFACE = 'vethfc9a5eb'  # Set this after running print_interfaces.py if needed
TARGET_PORT = 443

def is_tor_packet(pkt):
    if pkt.haslayer(Raw):
        try:
            payload = pkt[Raw].load
            data = json.loads(payload.decode(errors='ignore'))
            if data.get('is_tor', False):
                return True
            if isinstance(data.get('payload'), dict) and data['payload'].get('is_tor', False):
                return True
        except Exception:
            return False
    return False

def block_packet(pkt):
    ip = pkt[IP]
    tcp = pkt[TCP]
    rst1 = IP(src=ip.src, dst=ip.dst)/TCP(sport=tcp.sport, dport=tcp.dport, seq=tcp.seq, ack=tcp.ack, flags='R')
    rst2 = IP(src=ip.dst, dst=ip.src)/TCP(sport=tcp.dport, dport=tcp.sport, seq=tcp.ack, ack=tcp.seq+len(pkt[Raw].load), flags='R')
    send(rst1, verbose=0)
    send(rst2, verbose=0)
    print(f"[!] Blocked Tor packet from {ip.src}:{tcp.sport} to {ip.dst}:{tcp.dport}")

def packet_callback(pkt):
    # Log every packet
    proto = pkt.summary()
    print(f"[LOG] Packet seen: {proto}")
    # Print TCP payload if present
    if pkt.haslayer(Raw):
        try:
            payload = pkt[Raw].load
            print(f"[PAYLOAD] {payload}")
        except Exception as e:
            print(f"[PAYLOAD ERROR] {e}")
    # Only process TCP packets for Tor detection/blocking
    if pkt.haslayer(TCP):
        if is_tor_packet(pkt):
            print(f"[ALERT] Tor packet detected! Taking action...")
            block_packet(pkt)

import os

if __name__ == "__main__":
    # Add iptables REDIRECT rule for TCP port 443 to redirect to local port 8080 (example)
    # Adjust port as needed for your censor/proxy setup
    redirect_port = 8080  # Change as needed
    try:
        os.system(f"iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to-port {redirect_port}")
        print(f"[+] iptables REDIRECT rule added: TCP 443 -> {redirect_port}")
    except Exception as e:
        print(f"[!] Failed to add iptables REDIRECT rule: {e}")

    print("Available interfaces:", get_if_list())
    print(f"[*] Censor running on interface {INTERFACE}, watching ALL packets and blocking Tor traffic...")
    sniff(iface=INTERFACE, prn=packet_callback, store=0)
