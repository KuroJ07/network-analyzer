import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console

console = Console()

# Common ports and what service usually runs on them
COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    139: "NetBIOS",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    3306: "MySQL",
    3389: "RDP",
    5900: "VNC",
    8080: "HTTP-Alt",
    8443: "HTTPS-Alt",
}

# Ports that are worth flagging as risky if open
RISKY_PORTS = {23, 21, 3389, 5900, 139, 445}


def scan_port(ip: str, port: int, timeout: float = 0.5) -> dict | None:
    """
    Attempt to connect to a single port on a host.
    Returns port info if open, None if closed.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((ip, port))
        s.close()

        if result == 0:
            service = COMMON_PORTS.get(port, "Unknown")
            risky = port in RISKY_PORTS
            return {
                "port": port,
                "service": service,
                "risky": risky
            }
    except Exception:
        pass
    return None


def scan_ports(ip: str) -> list[dict]:
    """
    Scan all common ports on a host in parallel.
    Returns a list of open ports.
    """
    open_ports = []

    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {
            executor.submit(scan_port, ip, port): port
            for port in COMMON_PORTS
        }
        for future in as_completed(futures):
            result = future.result()
            if result:
                open_ports.append(result)

    return sorted(open_ports, key=lambda x: x["port"])
    