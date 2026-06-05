from scapy.all import sniff, ARP, DNS, DNSQR, IP, TCP, UDP, ICMP
from rich.console import Console
from rich.table import Table
from datetime import datetime
import threading

console = Console()

# Store captured packets as structured events
captured_events = []
capture_lock = threading.Lock()


def process_packet(packet) -> dict | None:
    """
    Inspect a single packet and extract meaningful info.
    Returns a structured event dict or None if not interesting.
    """
    event = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "protocol": "Unknown",
        "src": "",
        "dst": "",
        "info": ""
    }

    try:
        # ARP — device discovery and MAC resolution
        if packet.haslayer(ARP):
            arp = packet[ARP]
            if arp.op == 1:  # who-has (request)
                event["protocol"] = "ARP"
                event["src"] = arp.psrc
                event["dst"] = arp.pdst
                event["info"] = f"Who has {arp.pdst}? Tell {arp.psrc}"
            elif arp.op == 2:  # is-at (reply)
                event["protocol"] = "ARP"
                event["src"] = arp.psrc
                event["dst"] = arp.pdst
                event["info"] = f"{arp.psrc} is at {arp.hwsrc}"

        # DNS — domain name lookups
        elif packet.haslayer(DNS) and packet.haslayer(DNSQR):
            dns = packet[DNSQR]
            ip = packet[IP] if packet.haslayer(IP) else None
            event["protocol"] = "DNS"
            event["src"] = ip.src if ip else "?"
            event["dst"] = ip.dst if ip else "?"
            event["info"] = f"Query: {dns.qname.decode().rstrip('.')}"

        # ICMP — ping traffic
        elif packet.haslayer(ICMP):
            ip = packet[IP]
            icmp_type = packet[ICMP].type
            event["protocol"] = "ICMP"
            event["src"] = ip.src
            event["dst"] = ip.dst
            event["info"] = "Echo Request" if icmp_type == 8 else "Echo Reply"

        # TCP — general TCP connections
        elif packet.haslayer(TCP) and packet.haslayer(IP):
            tcp = packet[TCP]
            ip = packet[IP]
            flags = tcp.sprintf("%flags%")
            event["protocol"] = "TCP"
            event["src"] = f"{ip.src}:{tcp.sport}"
            event["dst"] = f"{ip.dst}:{tcp.dport}"
            event["info"] = f"Flags: {flags}"

        # UDP — general UDP traffic
        elif packet.haslayer(UDP) and packet.haslayer(IP):
            udp = packet[UDP]
            ip = packet[IP]
            event["protocol"] = "UDP"
            event["src"] = f"{ip.src}:{udp.sport}"
            event["dst"] = f"{ip.dst}:{udp.dport}"
            event["info"] = f"Len: {udp.len}"

        else:
            return None

    except Exception:
        return None

    return event


def capture_packets(count: int = 50, timeout: int = 30) -> list[dict]:
    """
    Capture packets from the network interface.
    count: max packets to capture
    timeout: stop after this many seconds regardless
    """
    console.print(f"\n[bold cyan]Capturing up to {count} packets "
                  f"(timeout: {timeout}s)...[/bold cyan]")
    console.print("[dim]Browse the web or ping something to generate traffic[/dim]\n")

    events = []

    def handle_packet(packet):
        event = process_packet(packet)
        if event:
            with capture_lock:
                events.append(event)

    sniff(prn=handle_packet, count=count, timeout=timeout, store=False)
    return events
    