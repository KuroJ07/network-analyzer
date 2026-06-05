# Network Analyzer

A home network scanner and analyzer built while studying for CompTIA Network+.

This project is built in phases, each one adding more capability while reinforcing
networking concepts like IP addressing, subnetting, port scanning, and packet analysis.

---

## Features

### Phase 1 — Host Discovery ✅
- Detects your local IP and subnet automatically
- Scans all 254 hosts in your /24 subnet using ICMP ping
- Resolves hostnames via reverse DNS
- Displays results in a formatted table
- Parallel scanning with 50 threads for speed

### Phase 2 — Port Scanner (coming soon)
- Scan open ports on discovered hosts
- Identify running services by port number
- Flag potentially risky open ports

### Phase 3 — Packet Analysis (coming soon)
- Capture and parse live network traffic
- Identify protocols in use (ARP, DNS, ICMP, TCP, UDP)
- Live traffic dashboard

### Phase 4 — Monitoring & Alerts (coming soon)
- Detect new devices joining the network
- Alert on unexpected open ports
- Log traffic anomalies over time

---

## Tech Stack

- **Language:** Python 3.13
- **Libraries:** Scapy, Rich
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

```bash
cd src
python main.py
```

---

## Project Structure

---

## What I Learned

This section grows as the project does. Updated after each phase.

### Phase 1
- ICDR /24 subnets contain 254 usable host addresses
- ICMP Echo Request/Reply is the protocol behind ping
- Reverse DNS (PTR records) maps IP addresses back to hostnames
- ThreadPoolExecutor allows parallel execution — scanning 50 hosts
  simultaneously instead of one at a time

---

## Disclaimer

This tool is built for use on your own home network only.
Scanning networks without permission is illegal.