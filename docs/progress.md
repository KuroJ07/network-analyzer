# Development Progress

A running log of what was built, decisions made, and concepts learned.

---

## Phase 1 — Host Discovery
**Status:** ✅ Complete

### What was built
- `src/utils/network.py` — detects local IP using a UDP socket trick,
  calculates subnet in CIDR notation
- `src/scanners/host_scanner.py` — pings all hosts in the subnet in parallel,
  resolves hostnames via reverse DNS
- `src/main.py` — entry point, ties everything together and displays
  results in a Rich table

### Key decisions
- Used `subprocess` to call the system ping instead of Scapy for Phase 1
  (simpler, no root/admin required)
- Set ThreadPoolExecutor to 50 workers — fast enough without hammering
  the network
- Used Rich library for clean terminal output

### Network+ concepts this covers
- IP addressing and subnetting (CIDR /24)
- ICMP protocol (ping = Echo Request / Echo Reply)
- DNS and reverse DNS (PTR records)
- Network host ranges and broadcast addresses

### Problems solved
- ImportError on utils.network — file had not been saved correctly in VS Code.
  Fixed by verifying file contents and re-saving with Ctrl+S.
- PowerShell vs CMD difference — `type nul >` does not work in PowerShell,
  replaced with `New-Item filename -Type File`

---

## Phase 2 — Port Scanner
**Status:** 🔲 Not started