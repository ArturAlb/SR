from scapy.all import IP, TCP
from netfilterqueue import NetfilterQueue
from datetime import datetime

LOG_FILE = "/var/log/censor.txt"  

def log_packet(action, ip_pkt, reason=None):
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    src = f"{ip_pkt.src}:{ip_pkt[TCP].sport}" if ip_pkt.haslayer(TCP) else ip_pkt.src
    dst = f"{ip_pkt.dst}:{ip_pkt[TCP].dport}" if ip_pkt.haslayer(TCP) else ip_pkt.dst
    log_msg = f"[{timestamp}] {action.upper()} packet from {src} to {dst}"
    if reason:
        log_msg += f" - Reason: {reason}"
    
    print(log_msg)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(log_msg + "\n")
    except Exception as e:
        print(f"Logging error: {e}")

def process_packet(pkt):
    scapy_pkt = IP(pkt.get_payload())
    
    if scapy_pkt.haslayer(TCP):
        tcp_payload = bytes(scapy_pkt[TCP].payload)
        
        if tcp_payload:
            try:
                payload_str = tcp_payload.decode(errors='ignore')
                if '"is_tor": true' in payload_str.lower():
                    log_packet("dropped", scapy_pkt, reason="Detected is_tor: true")
                    pkt.drop()
                    return
            except Exception as e:
                log_packet("passed", scapy_pkt, reason=f"Decode error: {e}")
                pkt.accept()
                return

    # Default accept
    log_packet("passed", scapy_pkt)
    pkt.accept()

nfqueue = NetfilterQueue()
nfqueue.bind(1, process_packet)

try:
    print("[*] Starting packet inspection with logging...")
    nfqueue.run()
except KeyboardInterrupt:
    print("[*] Stopping...")
    nfqueue.unbind()
