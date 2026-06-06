# Development Progress

A running log of what was built, decisions made, and concepts learned.

---

## Phase 1 — Host Discovery
**Status:**  Complete

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
**Status:**  Complete

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
- My own machine (10.0.0.xxx) has ports 139 (NetBIOS) and 445 (SMB) open
- These are Windows file sharing ports and a known attack surface
- SMB port 445 was exploited in the 2017 WannaCry ransomware attack

---

## Phase 3 — Packet Capture
**Status:**  Complete

### What was built
- `src/scanners/packet_capture.py` — captures live packets using Scapy,
  identifies ARP, DNS, ICMP, TCP, and UDP traffic
- Updated `src/main.py` — added optional packet capture prompt after
  host and port scanning

### Key decisions
- Used Scapy's sniff() with a timeout and packet count limit to keep
  capture controlled and safe
- Filtered for meaningful protocols only — ignored raw/unknown packets
- Required admin/root privileges — documented as a known requirement

### Network+ concepts this covers
- Packet structure and protocol layers (Layer 2, 3, 4)
- TCP flags — SYN, ACK, PSH, FIN and what they mean
- UDP vs TCP — connectionless vs connection-oriented
- mDNS (port 5353) — how devices discover each other without central DNS
- Multicast addressing — 224.0.0.251 is the mDNS multicast group
- Broadcast addressing — 255.255.255.255 reaches all hosts on the network

### Real findings from capture
- 10.0.0.xxx is an LG webOS TV broadcasting via mDNS/AirPlay on port 5353
- 10.0.0.xxx is a Google Cast device (Chromecast) — PC actively talking
  to it on port 8009
- 10.0.0.xxx is an Apple device advertising _companion-link (AirPlay/Handoff)
- A device broadcast to 255.255.255.255:9999 — likely a TP-Link smart
  home device

---

## Security Findings & Remediation
**Status:**  Complete

### Finding 1 — NetBIOS (Port 139)
- **Severity:** Medium
- **Found on:** 10.0.0.xxx (own machine, IP redacted)
- **What it is:** NetBIOS over TCP/IP — a legacy Windows networking protocol
  used for name resolution and file sharing on older networks
- **Why it's risky:** Unnecessary attack surface, used in older exploits like
  EternalBlue. Not needed on a single-user home machine with no file sharing.
- **Fix:** Disabled NetBIOS over TCP/IP via Network Adapter settings →
  TCP/IPv4 → Advanced → WINS tab → Disable NetBIOS over TCP/IP
- **Result:** Port 139 no longer appears in scan results ✅
- **Reversible:** Yes — same WINS tab, set back to Default or Enable

### Finding 2 — SMB (Port 445)
- **Severity:** Low (in current configuration)
- **Found on:** 10.0.0.xxx (own machine, IP redacted)
- **What it is:** SMB 2/3 (Server Message Block) — Windows file sharing protocol
- **Why it's worth noting:** Port 445 was the attack vector for the 2017
  WannaCry ransomware attack via SMB 1.0. However SMB 1.0 was already disabled
  on this machine. SMB 2/3 is significantly more secure.
- **Decision:** Left enabled. SMB 1.0 is disabled, SMB 2/3 risk is low on a
  home network with no active file sharing. Disabling SMB 2/3 entirely is an
  option via PowerShell but unnecessary given the current threat model.
- **Lesson:** Security decisions require context. Closing every open port isn't
  always the right call — understanding *why* something is open matters more.

---

## Phase 4 — Device Monitoring & Alerts
**Status:**  Complete

### What was built
- `src/utils/db.py` — SQLite database helper, creates and manages two tables:
  devices (known hosts) and events (join/leave log)
- `src/scanners/monitor.py` — continuous monitor that scans on an interval,
  detects changes, and alerts on new or leaving devices
- Updated `src/main.py` — added a menu system so the user can choose which
  mode to run

  ## MAC Address & Vendor Lookup
**Status:**  Complete

### What was built
- Updated `src/scanners/host_scanner.py` — after ping sweep, reads ARP cache
  to get each device's MAC address, then queries macvendors.com API to identify
  the manufacturer

### Network+ concepts this covers
- MAC addresses and OUI (Organizationally Unique Identifier)
- ARP cache — how the OS maps IP addresses to MAC addresses
- MAC randomization — modern devices (Apple, Android) rotate MAC addresses
  for privacy, which is why some vendors show as Unknown

### Real findings
- 10.0.0.xxx — Commscope (Xfinity router/modem)
- 10.0.0.xxx — Wyze Labs (smart home camera)
- 10.0.0.xxx — Beijing Roborock Technology (robot vacuum)
- Several devices show Unknown Vendor due to MAC randomization

### Key decisions
- Used SQLite for persistence — no external database needed, file-based,
  portable, and standard in Python
- Set scan interval to 60 seconds — frequent enough to catch changes,
  not so aggressive it hammers the network
- Distinguished between "new device never seen before" vs "known device
  rejoined" — different alert levels for each

### Network+ concepts this covers
- Network baselining — knowing what's normal so you can spot what isn't
- Device lifecycle on a network — DHCP lease, sleep/wake cycles
- Persistent logging — how network monitoring tools like SIEM work
- Broadcast domain — all devices visible within the /24 subnet

### Real findings from monitor
- 9 devices tracked and persisted to database on first run
- 10.0.0.xxx (Apple device) detected joining the network between scan #1
  and scan #2, then leaving by scan #3 — a real sleep/wake cycle caught
  in real time
- Full timestamped event log recorded for all activity
