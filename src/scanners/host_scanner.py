import subprocess
import ipaddress
import socket
import re
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console
from rich.progress import track
import requests

DEVICES_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "devices.json")


def load_nicknames() -> dict:
    """Load device nicknames from the local devices.json file."""
    try:
        with open(DEVICES_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

console = Console()


def get_mac_address(ip: str) -> str | None:
    """
    Get the MAC address of a device by checking the ARP cache.
    Works after a ping has been sent to the device.
    """
    try:
        result = subprocess.run(
            ["arp", "-a", ip],
            capture_output=True,
            text=True
        )
        # Extract MAC address from ARP output
        mac_pattern = r"([0-9a-fA-F]{2}[-:]){5}[0-9a-fA-F]{2}"
        match = re.search(mac_pattern, result.stdout)
        if match:
            return match.group(0).replace("-", ":").upper()
    except Exception:
        pass
    return None


def get_vendor(mac: str) -> str:
    """
    Look up the manufacturer of a device by its MAC address.
    Uses the macvendors.com free API.
    """
    try:
        response = requests.get(
            f"https://api.macvendors.com/{mac}",
            timeout=3
        )
        if response.status_code == 200:
            return response.text.strip()
    except Exception:
        pass
    return "Unknown Vendor"


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
    Then enriches each result with MAC address and vendor info.
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

    # Load nicknames
    nicknames = load_nicknames()

    # Enrich with MAC, vendor, and nickname
    console.print("\n[bold cyan]Looking up device vendors...[/bold cyan]\n")
    for host in online_hosts:
        mac = get_mac_address(host["ip"])
        host["mac"] = mac or "Unknown"
        host["vendor"] = get_vendor(mac) if mac else "Unknown"
        host["nickname"] = nicknames.get(host["ip"], "Unknown Device")

    return online_hosts