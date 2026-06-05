from rich.console import Console
from rich.table import Table
from scanners.host_scanner import scan_subnet
from utils.network import get_local_ip, get_subnet

console = Console()


def display_results(hosts: list[dict]) -> None:
    """Display scan results in a formatted table."""
    table = Table(title="Network Scan Results")

    table.add_column("IP Address", style="cyan", no_wrap=True)
    table.add_column("Hostname", style="green")
    table.add_column("Status", style="bold green")

    for host in sorted(hosts, key=lambda x: x["ip"]):
        table.add_row(host["ip"], host["hostname"], "● Online")

    console.print(table)
    console.print(f"\n[bold]Found {len(hosts)} online host(s)[/bold]")


def main():
    console.print("[bold green]Network Analyzer v0.1[/bold green]")
    console.print("[dim]Phase 1 — Host Discovery[/dim]\n")

    local_ip = get_local_ip()
    console.print(f"[*] Your IP: [cyan]{local_ip}[/cyan]")

    subnet = get_subnet(local_ip)
    console.print(f"[*] Scanning subnet: [cyan]{subnet}[/cyan]")

    hosts = scan_subnet(subnet)

    if not hosts:
        console.print("[red]No hosts found.[/red]")
        return

    display_results(hosts)


if __name__ == "__main__":
    main()
    