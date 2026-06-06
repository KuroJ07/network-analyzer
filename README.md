# Network Analyzer

A home network scanner and analyzer built while studying for CompTIA Network+.

This project is built in phases, each one adding more capability while reinforcing
networking concepts like IP addressing, subnetting, port scanning, and packet analysis.

---

## Features

### Phase 1 — Host Discovery 
- Detects your local IP and subnet automatically
- Scans all 254 hosts in your /24 subnet using ICMP ping
- Resolves hostnames via reverse DNS
- Displays results in a formatted table
- Parallel scanning with 50 threads for speed

### Phase 2 — Port Scanner 
- Scans 16 common ports on each live host
- Identifies running services by port number
- Flags potentially risky open ports (SMB, RDP, Telnet, VNC)
- Found and remediated real open ports on my own machine

### Phase 3 — Packet Capture 
- Captures live network traffic using Scapy
- Identifies protocols in use: ARP, DNS, ICMP, TCP, UDP
- Decodes mDNS device advertisements and DNS queries
- Displays a protocol summary after each capture session

### Phase 4 — Device Monitoring & Alerts 
- Continuously monitors the network on a configurable interval
- Detects new devices joining or leaving the network in real time
- Persists device history and event log to a local SQLite database
- Distinguishes between new devices never seen before vs known devices rejoining

---

## Tech Stack

- **Language:** Python 3.13
- **Libraries:** Scapy, Rich
- **Database:** SQLite (via Python's built-in sqlite3)
- **OS:** Windows (Npcap required for packet capture)

---

## Setup

### Prerequisites
- Python 3.10+
- [Npcap](https://npcap.com/#download) installed on Windows

### Installation

```bash
git clone https://github.com/KuroJ07/network-analyzer.git
cd network-analyzer
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Run

```
cd src
python main.py
```

You will be prompted

- **1** — Full scan (host discovery + port scanning)
- **2** — Packet capture only
- **3** — Continuous network monitor
- **4** — Full scan + packet capture

> Note: Packet capture and monitoring require running PowerShell as Administrator.

---

## Project Structure

```
network-analyzer/
├── src/
│   ├── scanners/
│   │   ├── host_scanner.py     # ICMP ping sweep
│   │   ├── port_scanner.py     # TCP port scanner with risk flagging
│   │   ├── packet_capture.py   # Live packet capture and analysis
│   │   └── monitor.py          # Continuous network monitor
│   ├── utils/
│   │   ├── network.py          # IP and subnet helpers
│   │   └── db.py               # SQLite database helper
│   └── main.py                 # Entry point and menu
├── docs/
│   └── progress.md             # Development log and findings
├── tests/
├── requirements.txt
└── README.md
```

---

## What I Learned

### Phase 1
- CIDR /24 subnets contain 254 usable host addresses
- ICMP Echo Request/Reply is the protocol behind ping
- Reverse DNS (PTR records) maps IP addresses back to hostnames
- ThreadPoolExecutor allows parallel execution — scanning 50 hosts simultaneously

### Phase 2
- TCP connect_ex() tests ports without completing a full connection
- Well-known ports (0-1023) map to standard services
- SMB (445) and NetBIOS (139) are common Windows attack surfaces
- Found ports 139 and 445 open on my own machine — researched and remediated

### Phase 3
- Packets are structured in layers — Ethernet → IP → TCP/UDP → Application
- mDNS (port 5353) is how devices advertise themselves without a central DNS server
- Multicast address 224.0.0.251 is used for local network service discovery
- TCP flags (SYN, ACK, PSH, FIN) indicate the state of a connection

### Phase 4
- Network baselining means knowing what's normal so anomalies stand out
- SQLite is a lightweight, file-based database built into Python — no server needed
- Caught a real device sleep/wake cycle during monitoring — Apple device joined
  and left within two 60-second scan intervals

---

## Security Findings

During development this tool was used on my own home network and produced real findings:

- **Port 139 (NetBIOS)** — found open, disabled via Windows network adapter settings
- **Port 445 (SMB)** — found open, SMB 1.0 already disabled, SMB 2/3 left enabled
  after research showed low risk on a home network with no active file sharing

Full details in [docs/progress.md](docs/progress.md).

---

## Disclaimer

This tool is built for use on your own home network only.
Scanning networks without explicit permission is illegal.