import subprocess
import ipaddress
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console
from rich.progress import track

console = Console()


def ping_host(ip: str) -> dict | None:
    """
    Ping a single IP. Returns a dict with host info if alive, None if not.
    """
    result = subprocess.run(
        ["ping", "-n", "1", "-w", "500", str(ip)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    if result.returncode == 0:
        # Try to resolve hostname
        try:
            hostname = socket.gethostbyaddr(str(ip))[0]
        except socket.herror:
            hostname = "Unknown"

        return {
            "ip": str(ip),
            "hostname": hostname,
            "status": "online"
        }
    return None


def scan_subnet(subnet: str) -> list[dict]:
    """
    Scan all hosts in a subnet using parallel pings.
    Returns a list of online hosts.
    """
    network = ipaddress.IPv4Network(subnet, strict=False)
    hosts = list(network.hosts())

    console.print(f"\n[bold cyan]Scanning {subnet} ({len(hosts)} hosts)...[/bold cyan]\n")

    online_hosts = []

    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(ping_host, ip): ip for ip in hosts}
        for future in track(as_completed(futures), total=len(futures), description="Scanning"):
            result = future.result()
            if result:
                online_hosts.append(result)

    return online_hosts
    