from rich.console import Console
from rich.table import Table
from scanners.host_scanner import scan_subnet
from scanners.port_scanner import scan_ports
from utils.network import get_local_ip, get_subnet

console = Console()


def display_hosts(hosts: list[dict]) -> None:
    """Display scan results in a formatted table."""
    table = Table(title="Online Hosts")
    table.add_column("IP Address", style="cyan", no_wrap=True)
    table.add_column("Hostname", style="green")
    table.add_column("Status", style="bold green")

    for host in sorted(hosts, key=lambda x: x["ip"]):
        table.add_row(host["ip"], host["hostname"], "● Online")

    console.print(table)
    console.print(f"\n[bold]Found {len(hosts)} online host(s)[/bold]\n")


def display_ports(ip: str, ports: list[dict]) -> None:
    """Display open ports for a host."""
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


def main():
    console.print("[bold green]Network Analyzer v0.2[/bold green]")
    console.print("[dim]Phase 1 + 2 — Host Discovery & Port Scanning[/dim]\n")

    local_ip = get_local_ip()
    console.print(f"[*] Your IP: [cyan]{local_ip}[/cyan]")

    subnet = get_subnet(local_ip)
    console.print(f"[*] Scanning subnet: [cyan]{subnet}[/cyan]")

    # Phase 1 - find live hosts
    hosts = scan_subnet(subnet)

    if not hosts:
        console.print("[red]No hosts found.[/red]")
        return

    display_hosts(hosts)

    # Phase 2 - scan ports on each live host
    console.print("[bold cyan]Scanning ports on live hosts...[/bold cyan]\n")

    for host in sorted(hosts, key=lambda x: x["ip"]):
        console.print(f"[*] Scanning [cyan]{host['ip']}[/cyan] ({host['hostname']})")
        ports = scan_ports(host["ip"])
        display_ports(host["ip"], ports)


if __name__ == "__main__":
    main()
    