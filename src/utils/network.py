import socket
import ipaddress


def get_local_ip() -> str:
    """Get the local machine's IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"


def get_subnet(ip: str, prefix: int = 24) -> str:
    """
    Given an IP, return the subnet in CIDR notation.
    Default is /24 (e.g. 192.168.1.0/24)
    """
    network = ipaddress.IPv4Network(f"{ip}/{prefix}", strict=False)
    return str(network)
    