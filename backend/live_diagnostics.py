import platform
import subprocess
import socket
import re
import statistics


def run_ping(host="8.8.8.8", count=4):
    """Measure latency and packet loss using the system ping command."""

    system = platform.system()

    if system == "Windows":
        command = ["ping", "-n", str(count), host]
    else:
        command = ["ping", "-c", str(count), host]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=15
        )

        output = result.stdout + result.stderr

        times = re.findall(r"time[=<]\s*(\d+(?:\.\d+)?)\s*ms", output)

        if system == "Windows":
            loss_match = re.search(r"\((\d+)%\s*loss\)", output)
        else:
            loss_match = re.search(r"(\d+(?:\.\d+)?)%\s*packet loss", output)

        packet_loss = float(loss_match.group(1)) if loss_match else None

        latency = (
            round(statistics.mean(map(float, times)), 2)
            if times else None
        )

        return {
            "host": host,
            "latency_ms": latency,
            "packet_loss_percent": packet_loss,
            "successful_replies": len(times),
            "status": "Reachable" if times else "Unreachable"
        }

    except subprocess.TimeoutExpired:
        return {
            "host": host,
            "latency_ms": None,
            "packet_loss_percent": None,
            "successful_replies": 0,
            "status": "Timeout"
        }

    except Exception as error:
        return {
            "host": host,
            "latency_ms": None,
            "packet_loss_percent": None,
            "successful_replies": 0,
            "status": "Error",
            "message": str(error)
        }


def check_dns(hostname="google.com"):
    """Check whether a domain name can be resolved."""

    try:
        ip_address = socket.gethostbyname(hostname)

        return {
            "hostname": hostname,
            "ip_address": ip_address,
            "status": "Working"
        }

    except socket.gaierror:
        return {
            "hostname": hostname,
            "ip_address": None,
            "status": "Failed"
        }


def get_default_gateway():
    """Find the default gateway on Windows."""

    if platform.system() != "Windows":
        return None

    try:
        result = subprocess.run(
            ["ipconfig"],
            capture_output=True,
            text=True,
            timeout=10
        )

        lines = result.stdout.splitlines()

        for index, line in enumerate(lines):
            if "Default Gateway" in line:
                match = re.search(
                    r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
                    line
                )

                if match:
                    return match.group(0)

                if index + 1 < len(lines):
                    match = re.search(
                        r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
                        lines[index + 1]
                    )

                    if match:
                        return match.group(0)

        return None

    except Exception:
        return None


def run_live_diagnostics():
    """Run all live network diagnostic checks."""

    print("\n========== NETFIX AI LIVE NETWORK DIAGNOSTICS ==========\n")

    internet = run_ping("8.8.8.8")
    print("Internet Connectivity:", internet)

    dns = check_dns()
    print("DNS Resolution:", dns)

    gateway_ip = get_default_gateway()

    if gateway_ip:
        gateway = run_ping(gateway_ip)
        gateway["gateway_ip"] = gateway_ip
    else:
        gateway = {
            "gateway_ip": None,
            "status": "Not Found"
        }

    print("Gateway Connectivity:", gateway)

    report = {
        "internet": internet,
        "dns": dns,
        "gateway": gateway
    }

    return report


if __name__ == "__main__":
    run_live_diagnostics()


def run_traceroute(host="8.8.8.8", max_hops=12):
    """Trace the network route to a destination."""

    system = platform.system()

    if system == "Windows":
        command = [
            "tracert",
            "-d",
            "-h", str(max_hops),
            "-w", "1000",
            host
        ]
    else:
        command = [
            "traceroute",
            "-n",
            "-m", str(max_hops),
            "-w", "1",
            host
        ]

    hops = []

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=max_hops * 4 + 10
        )

        output = result.stdout + result.stderr

        for line in output.splitlines():

            hop_match = re.match(r"^\s*(\d+)\s+(.+)$", line)

            if not hop_match:
                continue

            hop_number = int(hop_match.group(1))
            hop_details = hop_match.group(2)

            times = re.findall(r"(\d+(?:\.\d+)?)\s*ms", hop_details)

            ip_match = re.search(
                r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
                hop_details
            )

            hops.append({
                "hop": hop_number,
                "ip_address": ip_match.group(0) if ip_match else None,
                "response_times_ms": [float(value) for value in times],
                "average_latency_ms": (
                    round(statistics.mean(map(float, times)), 2)
                    if times else None
                ),
                "status": "Responding" if times else "No Response"
            })

        return {
            "destination": host,
            "total_hops": len(hops),
            "hops": hops,
            "status": "Completed" if hops else "No Route Information"
        }

    except subprocess.TimeoutExpired:
        return {
            "destination": host,
            "total_hops": len(hops),
            "hops": hops,
            "status": "Timeout"
        }

    except Exception as error:
        return {
            "destination": host,
            "total_hops": len(hops),
            "hops": hops,
            "status": "Error",
            "message": str(error)
        }

