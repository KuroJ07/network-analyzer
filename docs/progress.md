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
## Phase 2 — Port Scanner
**Status:** ✅ Complete

### What was built
- `src/scanners/port_scanner.py` — scans 16 common ports on each live host,
  identifies services by port number, flags risky ports
- Updated `src/main.py` — now runs port scan on every host found in Phase 1

### Key decisions
- Used `socket.connect_ex()` instead of a full connection — returns an error
  code rather than raising an exception, cleaner for scanning
- Hardcoded 16 well-known ports for now rather than scanning all 65535
  (faster, less noisy, enough for Phase 2)
- Flagged ports 21, 23, 139, 445, 3389, 5900 as risky based on common
  attack surface

### Network+ concepts this covers
- TCP three-way handshake (what connect_ex is actually testing)
- Well-known ports (0-1023) vs registered ports
- Common services and their port numbers
- SMB, NetBIOS, RDP, VNC — common attack vectors

### Real finding
- My own machine (10.0.0.187) has ports 139 (NetBIOS) and 445 (SMB) open
- These are Windows file sharing ports and a known attack surface
- SMB port 445 was exploited in the 2017 WannaCry ransomware attack

---

## Phase 3 — Packet Analysis
**Status:** 🔲 Not started