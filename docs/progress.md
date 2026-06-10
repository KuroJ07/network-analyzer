# Development Progress

A running log of what was built, decisions made, and concepts learned.

Project Start: June 6, 2026
Project Complete: June 9, 2026
Total Time: ~3 days, single session hands-on build

---

## Phase 1 — Host Discovery

Status: Complete

### What was built

- `src/utils/network.py` — detects the local IP using a UDP socket trick and calculates the subnet in CIDR notation
- `src/scanners/host_scanner.py` — pings all hosts in the subnet in parallel and resolves hostnames via reverse DNS
- `src/main.py` — entry point that ties everything together and displays results in a Rich table

### Key decisions

- Used subprocess to call the system ping instead of Scapy because it is simpler and does not require admin privileges
- Set ThreadPoolExecutor to 50 workers, fast enough without hammering the network
- Used the Rich library for clean terminal output

### Network+ concepts this covers

- IP addressing and subnetting (CIDR /24)
- ICMP protocol (ping = Echo Request / Echo Reply)
- DNS and reverse DNS (PTR records)
- Network host ranges and broadcast addresses

### Problems solved

- ImportError on utils.network because the file had not been saved correctly in VS Code, fixed by verifying file contents and re-saving with Ctrl+S
- PowerShell vs CMD difference, the type nul > command does not work in PowerShell, replaced with New-Item filename -Type File

---

## Phase 2 — Port Scanner

Status: Complete

### What was built

- `src/scanners/port_scanner.py` — scans 16 common ports on each live host, identifies services by port number, and flags risky ports
- Updated `src/main.py` — runs a port scan on every host found in Phase 1

### Key decisions

- Used socket.connect_ex() instead of a full connection because it returns an error code rather than raising an exception, cleaner for scanning
- Hardcoded 16 well-known ports rather than scanning all 65535, faster and less noisy
- Flagged ports 21, 23, 139, 445, 3389, and 5900 as risky based on common attack surface

### Network+ concepts this covers

- TCP three-way handshake (what connect_ex is actually testing)
- Well-known ports (0-1023) vs registered ports
- Common services and their port numbers
- SMB, NetBIOS, RDP, VNC as common attack vectors

### Real finding

- My own machine had ports 139 (NetBIOS) and 445 (SMB) open
- These are Windows file sharing ports and a known attack surface
- SMB port 445 was exploited in the 2017 WannaCry ransomware attack

---

## Phase 3 — Packet Capture

Status: Complete

### What was built

- `src/scanners/packet_capture.py` — captures live packets using Scapy and identifies ARP, DNS, ICMP, TCP, and UDP traffic
- Updated `src/main.py` — added an optional packet capture prompt after host and port scanning

### Key decisions

- Used Scapy's sniff() with a timeout and packet count limit to keep capture controlled
- Filtered for meaningful protocols only, ignored raw or unknown packets
- Requires admin privileges on Windows, documented as a known requirement

### Network+ concepts this covers

- Packet structure and protocol layers (Layer 2, 3, 4)
- TCP flags (SYN, ACK, PSH, FIN) and what they mean
- UDP vs TCP, connectionless vs connection-oriented
- mDNS on port 5353 and how devices discover each other without a central DNS server
- Multicast addressing, 224.0.0.251 is the mDNS multicast group
- Broadcast addressing, 255.255.255.255 reaches all hosts on the network

### Real findings from capture

- An LG webOS TV was broadcasting via mDNS and AirPlay on port 5353
- A Google Cast device was actively communicating with my PC on port 8009
- An Apple device was advertising itself via the companion-link service used for AirPlay and Handoff
- A device broadcast to 255.255.255.255 on port 9999, consistent with a TP-Link smart home device

---

## Phase 4 — Device Monitoring and Alerts

Status: Complete

### What was built

- `src/utils/db.py` — SQLite database helper that creates and manages two tables, devices (known hosts) and events (join/leave log)
- `src/scanners/monitor.py` — continuous monitor that scans on a set interval, detects changes, and alerts on new or leaving devices
- Updated `src/main.py` — added a menu so the user can choose which mode to run

### Key decisions

- Used SQLite for persistence, no external database needed, file-based, portable, and built into Python
- Set scan interval to 60 seconds, frequent enough to catch changes without hammering the network
- Distinguished between a device never seen before vs a known device rejoining, different alert levels for each

### Network+ concepts this covers

- Network baselining, knowing what is normal so anomalies stand out
- Device lifecycle on a network, DHCP lease and sleep/wake cycles
- Persistent logging and how tools like SIEM work
- Broadcast domain, all devices visible within the /24 subnet

### Real findings from monitor

- 9 devices tracked and persisted to the database on first run
- The MacBook was detected joining the network between scan 1 and scan 2, then leaving by scan 3, a real sleep/wake cycle caught in real time
- Full timestamped event log recorded for all activity

---

## Security Findings and Remediation

Status: Complete

### Finding 1 — NetBIOS (Port 139)

Severity: Medium

- What it is: NetBIOS over TCP/IP, a legacy Windows networking protocol used for name resolution and file sharing on older networks
- Why it is risky: unnecessary attack surface, used in older exploits like EternalBlue, not needed on a single-user home machine with no file sharing
- Fix: disabled NetBIOS over TCP/IP via Network Adapter settings, TCP/IPv4, Advanced, WINS tab, Disable NetBIOS over TCP/IP
- Result: port 139 no longer appears in scan results
- Reversible: yes, same WINS tab, set back to Default or Enable

### Finding 2 — SMB (Port 445)

Severity: Low in current configuration

- What it is: SMB 2/3 (Server Message Block), the Windows file sharing protocol
- Why it is worth noting: port 445 was the attack vector for the 2017 WannaCry ransomware attack via SMB 1.0, however SMB 1.0 was already disabled on this machine and SMB 2/3 is significantly more secure
- Decision: left enabled, SMB 1.0 is disabled and SMB 2/3 risk is low on a home network with no active file sharing
- Lesson: security decisions require context, closing every open port is not always the right call, understanding why something is open matters more

---

## MAC Address and Vendor Lookup

Status: Complete

### What was built

- Updated `src/scanners/host_scanner.py` — after the ping sweep, reads the ARP cache to get each device's MAC address, then queries the macvendors.com API to identify the manufacturer

### Network+ concepts this covers

- MAC addresses and OUI (Organizationally Unique Identifier)
- ARP cache, how the OS maps IP addresses to MAC addresses
- MAC randomization, modern devices rotate MAC addresses for privacy which is why some vendors show as Unknown

### Real findings

- Commscope (Xfinity router/modem)
- Wyze Labs (Wyze Camera)
- Beijing Roborock Technology (Roborock Vacuum)
- Smart Innovation LLC (Eufy Device)
- Several devices show Unknown Vendor due to MAC randomization

---

## Email Alerts

Status: Complete

### What was built

- `src/utils/alerts.py` — sends email via Gmail SMTP when a device is detected joining the network
- Updated `src/scanners/monitor.py` — calls send_alert() after each join event
- `.env.example` — template showing required credentials without exposing real values

### Key decisions

- Used a Gmail App Password instead of the account password, more secure and can be revoked independently
- Credentials stored in a .env file which is gitignored and never touches GitHub
- Alert distinguishes between a truly new device vs a known device rejoining
- Gracefully skips alerting if credentials are not configured

### Network+ concepts this covers

- SMTP protocol (port 465 with SSL), how email is transmitted
- SSL/TLS, encrypting the connection to Gmail's mail server
- Application credentials and secure storage, never hardcode secrets

### Security practices

- .env file is gitignored, credentials never committed to version control
- .env.example committed instead, shows required variables without exposing real values
- App Password is scoped to this application only and can be revoked without changing the Gmail password

---

## Unit Tests

Status: Complete

### What was built

- `tests/test_network.py` — 10 tests covering get_local_ip() and get_subnet()
- `tests/test_port_scanner.py` — 8 tests covering scan_port() and port constants

### How to run

pytest tests/ -v

### What was tested

- get_local_ip() returns a valid non-empty IPv4 string
- get_subnet() correctly zeros host bits and respects custom prefix lengths
- scan_port() returns the correct structure when a port is open
- RISKY_PORTS is always a subset of COMMON_PORTS
- All key well-known ports are present in COMMON_PORTS

### Why tests matter

- Catches broken code before it runs on a real network
- Documents expected behavior, tests are a form of specification
- Industry standard, almost every professional codebase has a test suite
- 18 out of 18 passing on first run

---

## Web Dashboard

Status: Complete

### What was built

- `src/dashboard.py` — Flask web server with three API endpoints, /api/devices, /api/events, and /api/scan
- `src/templates/index.html` — single page dashboard showing live scan results, known devices, event history, and summary stats

### How to run

cd src
python dashboard.py

Then open http://127.0.0.1:5000 in a browser.

### Key decisions

- Kept the frontend as plain HTML and JavaScript, no React or Node needed, runs anywhere Python runs
- API endpoints return JSON so the dashboard can be replaced or extended without changing the backend
- Live scan runs on demand via a button, not automatic, to avoid hammering the network
- Nicknames from devices.json are displayed across all three tables

### What it shows

- Stats row showing total devices, online count, events logged, and risky ports
- Live scan table with IP, name, hostname, MAC, vendor, open ports, and risk status
- Known devices table with full history from the SQLite database and friendly names
- Recent events table with a timestamped join/leave log and friendly names
- Auto-refreshes devices and events every 30 seconds

---

## Device Nicknames

Status: Complete

### What was built

- `src/data/devices.json` — local inventory file mapping IP addresses to friendly device names, gitignored and never pushed to GitHub
- Updated `src/scanners/host_scanner.py` — loads nicknames and adds them to scan results
- Updated `src/dashboard.py` — passes nicknames to all three API endpoints
- Updated `src/templates/index.html` — displays nicknames in all three tables

### Key decisions

- File is gitignored because it contains real IP to device mappings and stays local
- Falls back to Unknown Device if the IP is not in the file
- Mirrors real network inventory management practices used in professional environments

### Devices identified

- Xfinity Router
- Wyze Camera
- Hisense TV
- Roborock Vacuum
- Eufy Device
- MacBook
- My PC
- Several devices still unknown, likely using MAC randomization

---

## Project Summary

| Feature | Status |
|---|---|
| Host discovery | Complete |
| Port scanning and risk flagging | Complete |
| Security findings and remediation | Complete |
| Packet capture and protocol analysis | Complete |
| Device monitoring with SQLite | Complete |
| MAC address and vendor lookup | Complete |
| Email alerts | Complete |
| Unit tests (18/18 passing) | Complete |
| Web dashboard | Complete |
| Device nicknames | Complete |
| Professional GitHub repo | Complete |

Total development time: ~3 days
Lines of code: ~800
Commits: 15+
Tests: 18 passing