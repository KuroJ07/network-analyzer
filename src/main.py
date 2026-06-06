from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from scanners.host_scanner import scan_subnet
from scanners.port_scanner import scan_ports
from scanners.packet_capture import capture_packets
from scanners.monitor import run_monitor
from utils.network import get_local_ip, get_subnet

console = Console()


def display_hosts(hosts: list[dict]) -> None:
    table = Table(title="Online Hosts")
    table.add_column("IP Address", style="cyan", no_wrap=True)
    table.add_column("Hostname", style="green")
    table.add_column("MAC Address", style="dim")
    table.add_column("Vendor", style="yellow")
    table.add_column("Status", style="bold green")

    for host in sorted(hosts, key=lambda x: x["ip"]):
        table.add_row(
            host["ip"],
            host["hostname"],
            host.get("mac", "Unknown"),
            host.get("vendor", "Unknown"),
            "● Online"
        )

    console.print(table)
    console.print(f"\n[bold]Found {len(hosts)} online host(s)[/bold]\n")


def display_ports(ip: str, ports: list[dict]) -> None:
    if not ports:
        console.print(f"[dim]No common ports open on {ip}[/dim]\n")
        return

    table = Table(title=f"Open Ports on {ip}")
    table.add_column("Port", style="cyan")
    table.add_column("Service", style="green")
    table.add_column("Risk", style="bold")

    for p in ports:
        risk = "[red]⚠ Risky[/red]" if p["risky"] else "[green]OK[/green]"
        table.add_row(str(p["port"]), p["service"], risk)

    console.print(table)
    console.print()


def display_packets(events: list[dict]) -> None:
    if not events:
        console.print("[red]No packets captured.[/red]")
        return

    table = Table(title="Captured Packets")
    table.add_column("Time", style="dim")
    table.add_column("Protocol", style="bold cyan")
    table.add_column("Source", style="green")
    table.add_column("Destination", style="yellow")
    table.add_column("Info", style="white")

    for e in events:
        table.add_row(e["time"], e["protocol"], e["src"], e["dst"], e["info"])

    console.print(table)
    console.print(f"\n[bold]Captured {len(events)} packets[/bold]\n")

    summary = {}
    for e in events:
        summary[e["protocol"]] = summary.get(e["protocol"], 0) + 1

    console.print("[bold cyan]Protocol Summary:[/bold cyan]")
    for proto, count in sorted(summary.items(), key=lambda x: -x[1]):
        console.print(f"  {proto}: {count} packets")


def main():
    console.print("[bold green]Network Analyzer v0.4[/bold green]")
    console.print("[dim]Home Network Scanner & Monitor[/dim]\n")

    console.print("What would you like to do?")
    console.print("  [cyan]1[/cyan] — Full scan (hosts + ports)")
    console.print("  [cyan]2[/cyan] — Packet capture only")
    console.print("  [cyan]3[/cyan] — Start network monitor")
    console.print("  [cyan]4[/cyan] — Full scan + packet capture")

    choice = Prompt.ask("\nChoice", choices=["1", "2", "3", "4"])

    local_ip = get_local_ip()
    subnet = get_subnet(local_ip)

    console.print(f"\n[*] Your IP: [cyan]{local_ip}[/cyan]")
    console.print(f"[*] Subnet: [cyan]{subnet}[/cyan]\n")

    if choice in ["1", "4"]:
        hosts = scan_subnet(subnet)
        if not hosts:
            console.print("[red]No hosts found.[/red]")
            return
        display_hosts(hosts)

        console.print("[bold cyan]Scanning ports on live hosts...[/bold cyan]\n")
        for host in sorted(hosts, key=lambda x: x["ip"]):
            console.print(f"[*] Scanning [cyan]{host['ip']}[/cyan] ({host['hostname']})")
            ports = scan_ports(host["ip"])
            display_ports(host["ip"], ports)

    if choice in ["2", "4"]:
        events = capture_packets(count=50, timeout=30)
        display_packets(events)

    if choice == "3":
        run_monitor(interval=60)


if __name__ == "__main__":
    main()
    