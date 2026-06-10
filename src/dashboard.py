from flask import Flask, render_template, jsonify
from utils.db import get_all_devices, get_recent_events
from utils.network import get_local_ip, get_subnet
from scanners.host_scanner import scan_subnet, load_nicknames
from scanners.port_scanner import scan_ports
import json

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/devices")
def api_devices():
    devices = get_all_devices()
    nicknames = load_nicknames()
    result = []
    for d in [dict(d) for d in devices]:
        d["nickname"] = nicknames.get(d["ip"], "Unknown Device")
        result.append(d)
    return jsonify(result)


@app.route("/api/events")
def api_events():
    events = get_recent_events(limit=50)
    nicknames = load_nicknames()
    result = []
    for e in [dict(e) for e in events]:
        e["nickname"] = nicknames.get(e["ip"], "Unknown Device")
        result.append(e)
    return jsonify(result)


@app.route("/api/scan")
def api_scan():
    local_ip = get_local_ip()
    subnet = get_subnet(local_ip)
    hosts = scan_subnet(subnet)
    for host in hosts:
        ports = scan_ports(host["ip"])
        host["ports"] = ports
    return jsonify({
        "subnet": subnet,
        "local_ip": local_ip,
        "hosts": hosts
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)