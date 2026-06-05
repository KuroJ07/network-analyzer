from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from scanners.host_scanner import scan_subnet
from scanners.port_scanner import scan_ports
from scanners.packet_capture import capture_packets
from utils.network import get_local_ip, get_subnet

console = Console()


def display_hosts(hosts: list[dict]) -> None:
    table = Table(title="Online Hosts")
    table.add_column("IP Address", style="cyan", no_wrap=True)
    table.add_column("Hostname", style="green")
    table.add_column("Status", style="bold green")

    for host in sorted(hosts, key=lambda x: x["ip"]):
        table.add_row(host["ip"], host["hostname"], "● Online")

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

    # Protocol summary
    summary = {}
    for e in events:
        summary[e["protocol"]] = summary.get(e["protocol"], 0) + 1

    console.print("[bold cyan]Protocol Summary:[/bold cyan]")
    for proto, count in sorted(summary.items(), key=lambda x: -x[1]):
        console.print(f"  {proto}: {count} packets")


def main():
    console.print("[bold green]Network Analyzer v0.3[/bold green]")
    console.print("[dim]Phase 1 + 2 + 3 — Host Discovery, Port Scanning & Packet Capture[/dim]\n")

    local_ip = get_local_ip()
    console.print(f"[*] Your IP: [cyan]{local_ip}[/cyan]")

    subnet = get_subnet(local_ip)
    console.print(f"[*] Scanning subnet: [cyan]{subnet}[/cyan]\n")

    # Phase 1
    hosts = scan_subnet(subnet)
    if not hosts:
        console.print("[red]No hosts found.[/red]")
        return
    display_hosts(hosts)

    # Phase 2
    console.print("[bold cyan]Scanning ports on live hosts...[/bold cyan]\n")
    for host in sorted(hosts, key=lambda x: x["ip"]):
        console.print(f"[*] Scanning [cyan]{host['ip']}[/cyan] ({host['hostname']})")
        ports = scan_ports(host["ip"])
        display_ports(host["ip"], ports)

    # Phase 3
    answer = Prompt.ask("\n[bold yellow]Run packet capture?[/bold yellow] (yes/no)")
    if answer.lower() == "yes":
        events = capture_packets(count=50, timeout=30)
        display_packets(events)


if __name__ == "__main__":
    main()
    