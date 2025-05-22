from scapy.all import sniff, send, IP, TCP, Raw, get_if_list
import json

# Adjust this to your network interface (use get_if_list() to print available interfaces)
INTERFACE = 'Ethernet'  # Change if needed
TARGET_PORT = 443

def is_tor_packet(pkt):
    if pkt.haslayer(Raw):
        try:
            payload = pkt[Raw].load
            # Try to decode as JSON (outermost layer)
            data = json.loads(payload.decode(errors='ignore'))
            # Check for the is_tor flag (direct or nested)
            if data.get('is_tor', False):
                return True
            # If payload is nested, check for 'payload' key
            if isinstance(data.get('payload'), dict) and data['payload'].get('is_tor', False):
                return True
        except Exception:
            return False
    return False

def block_packet(pkt):
    ip = pkt[IP]
    tcp = pkt[TCP]
    # Send TCP RST to both sides to kill the connection
    rst1 = IP(src=ip.src, dst=ip.dst)/TCP(sport=tcp.sport, dport=tcp.dport, seq=tcp.seq, ack=tcp.ack, flags='R')
    rst2 = IP(src=ip.dst, dst=ip.src)/TCP(sport=tcp.dport, dport=tcp.sport, seq=tcp.ack, ack=tcp.seq+len(pkt[Raw].load), flags='R')
    send(rst1, verbose=0)
    send(rst2, verbose=0)
    print(f"[!] Blocked Tor packet from {ip.src}:{tcp.sport} to {ip.dst}:{tcp.dport}")

def packet_callback(pkt):
    if pkt.haslayer(TCP) and pkt[TCP].dport == TARGET_PORT:
        if is_tor_packet(pkt):
            block_packet(pkt)

if __name__ == "__main__":
    print("Available interfaces:", get_if_list())
    print(f"[*] Censor running on interface {INTERFACE}, blocking Tor packets on port {TARGET_PORT}...")
    sniff(iface=INTERFACE, filter=f"tcp port {TARGET_PORT}", prn=packet_callback, store=0)
