import time
from datetime import datetime
from rich.console import Console
from rich.table import Table
from scanners.host_scanner import scan_subnet
from utils.network import get_local_ip, get_subnet
from utils.db import init_db, upsert_device, log_event, get_all_devices, get_recent_events
from utils.alerts import send_alert

console = Console()


def get_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def display_known_devices():
    """Display all devices seen on the network."""
    devices = get_all_devices()
    if not devices:
        console.print("[dim]No devices recorded yet.[/dim]")
        return

    table = Table(title="Known Devices")
    table.add_column("IP", style="cyan")
    table.add_column("Hostname", style="green")
    table.add_column("First Seen", style="dim")
    table.add_column("Last Seen", style="dim")
    table.add_column("Status", style="bold")

    for d in devices:
        status = "[green]Online[/green]" if d["status"] == "online" else "[red]Offline[/red]"
        table.add_row(d["ip"], d["hostname"], d["first_seen"], d["last_seen"], status)

    console.print(table)


def display_recent_events():
    """Display recent network events."""
    events = get_recent_events()
    if not events:
        console.print("[dim]No events recorded yet.[/dim]")
        return

    table = Table(title="Recent Events")
    table.add_column("Timestamp", style="dim")
    table.add_column("IP", style="cyan")
    table.add_column("Hostname", style="green")
    table.add_column("Event", style="bold")

    for e in events:
        if e["event_type"] == "joined":
            event_str = "[green]▲ Joined[/green]"
        elif e["event_type"] == "left":
            event_str = "[red]▼ Left[/red]"
        else:
            event_str = e["event_type"]

        table.add_row(e["timestamp"], e["ip"], e["hostname"], event_str)

    console.print(table)


def run_monitor(interval: int = 60):
    """
    Continuously scan the network and alert on changes.
    interval: seconds between scans
    """
    init_db()

    local_ip = get_local_ip()
    subnet = get_subnet(local_ip)

    console.print(f"\n[bold green]Starting Network Monitor[/bold green]")
    console.print(f"[*] Subnet: [cyan]{subnet}[/cyan]")
    console.print(f"[*] Scan interval: [cyan]{interval}s[/cyan]")
    console.print("[dim]Press Ctrl+C to stop[/dim]\n")

    # Track what was online in the previous scan
    previous_hosts = set()
    scan_count = 0

    try:
        while True:
            scan_count += 1
            timestamp = get_timestamp()
            console.print(f"[dim]── Scan #{scan_count} at {timestamp} ──[/dim]")

            # Scan the network
            hosts = scan_subnet(subnet)
            current_hosts = {h["ip"]: h for h in hosts}
            current_ips = set(current_hosts.keys())

            # Detect new devices
            new_devices = current_ips - previous_hosts
            for ip in new_devices:
                host = current_hosts[ip]
                is_new = upsert_device(ip, host["hostname"], timestamp)
                log_event(ip, host["hostname"], "joined", timestamp)
                if is_new:
                    console.print(
                        f"[bold green]⚠ NEW DEVICE:[/bold green] "
                        f"[cyan]{ip}[/cyan] ({host['hostname']}) — "
                        f"first time seen on this network"
                    )
                else:
                    console.print(
                        f"[green]▲ Joined:[/green] "
                        f"[cyan]{ip}[/cyan] ({host['hostname']})"
                    )

                # Send email alert
                sent = send_alert(ip, host["hostname"], timestamp, is_new)
                if sent:
                    console.print(f"[dim]  → Alert email sent[/dim]")

            # Detect devices that left
            left_devices = previous_hosts - current_ips
            for ip in left_devices:
                log_event(ip, "Unknown", "left", timestamp)
                console.print(f"[red]▼ Left:[/red] [cyan]{ip}[/cyan]")

            previous_hosts = current_ips

            # Show summary every 5 scans
            if scan_count % 5 == 0:
                console.print()
                display_known_devices()
                display_recent_events()

            console.print(f"[dim]Next scan in {interval}s...[/dim]\n")
            time.sleep(interval)

    except KeyboardInterrupt:
        console.print("\n[bold yellow]Monitor stopped.[/bold yellow]")
        console.print("\n[bold]Final Summary:[/bold]")
        display_known_devices()
        display_recent_events()
        