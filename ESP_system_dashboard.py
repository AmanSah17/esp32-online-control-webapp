import wifi
import socketpool
import gc
import time

# Wi-Fi setup
SSID = "Aman_4g"
PASSWORD = "amansah17"

print("📶 Connecting to Wi-Fi...")
wifi.radio.connect(SSID, PASSWORD)
print("✅ Connected to", SSID)
print("🌐 IP Address:", wifi.radio.ipv4_address)

pool = socketpool.SocketPool(wifi.radio)
server = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
server.setsockopt(pool.SOL_SOCKET, pool.SO_REUSEADDR, 1)
server.bind((str(wifi.radio.ipv4_address), 80))
server.listen(1)

start_time = time.monotonic()
error_log = []  # Store recent errors (up to 5)

def get_system_health():
    # Wi-Fi status
    wifi_status = "Connected" if wifi.radio.connected else "Disconnected"
    wifi_rssi = getattr(wifi.radio, 'rssi', None)  # Check if RSSI is available
    wifi_signal = f"{wifi_rssi} dBm" if wifi_rssi is not None else "Unknown"
    
    # Memory health (assume ~100KB total memory for ESP32)
    free_mem = gc.mem_free()
    total_mem = 51200  # Approximate total memory
    mem_percent = (free_mem / total_mem) * 100
    if mem_percent > 50:
        mem_health = "Healthy"
        mem_color = "green"
    elif mem_percent > 20:
        mem_health = "Warning"
        mem_color = "orange"
    else:
        mem_health = "Critical"
        mem_color = "red"
    
    # Uptime status
    uptime = time.monotonic() - start_time
    uptime_status = "Stable" if uptime > 60 else "Initializing"
    uptime_color = "green" if uptime > 60 else "blue"
    
    # Error status
    error_status = "No recent errors" if not error_log else f"{len(error_log)} recent error(s)"
    error_color = "green" if not error_log else "orange"
    
    # Overall health
    overall_status = "System Healthy"
    overall_color = "green"
    if wifi_status == "Disconnected" or mem_health == "Critical" or error_log:
        overall_status = "System Warning"
        overall_color = "orange"
    
    return {
        "wifi_status": wifi_status,
        "wifi_signal": wifi_signal,
        "mem_health": mem_health,
        "mem_percent": mem_percent,
        "mem_color": mem_color,
        "uptime": uptime,
        "uptime_status": uptime_status,
        "uptime_color": uptime_color,
        "error_status": error_status,
        "error_color": error_color,
        "overall_status": overall_status,
        "overall_color": overall_color
    }

def html_page():
    health = get_system_health()
    error_messages = ''.join([f'<p>{err}</p>' for err in error_log[-3:]])  # Show last 3 errors
    return f"""HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
    <title>ESP32 Dashboard</title>
    <style>
        body {{ font-family: Arial; text-align: center; background-color: #f4f4f4; }}
        .card {{ border: 1px solid #ccc; padding: 15px; margin: 10px; border-radius: 5px; background: white; }}
        .health-card {{ background: #f9f9f9; }}
        .status {{ color: white; padding: 5px; border-radius: 3px; display: inline-block; }}
        button {{ padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }}
        button:hover {{ background: #0056b3; }}
    </style>
</head>
<body>
    <h1>ESP32 System Dashboard</h1>
    <div class="card">
        <h2>System Information</h2>
        <p>IP Address: {wifi.radio.ipv4_address}</p>
        <p>Free Memory: {gc.mem_free()} bytes</p>
        <p>Uptime: {health['uptime']:.2f} seconds</p>
    </div>
    <div class="card health-card">
        <h2>System Health Check</h2>
        <p>Wi-Fi Status: <span class="status" style="background: {'green' if health['wifi_status'] == 'Connected' else 'red'}">{health['wifi_status']}</span></p>
        <p>Wi-Fi Signal: {health['wifi_signal']}</p>
        <p>Memory Health: <span class="status" style="background: {health['mem_color']}">{health['mem_health']} ({health['mem_percent']:.1f}% free)</span></p>
        <p>Uptime Status: <span class="status" style="background: {health['uptime_color']}">{health['uptime_status']}</span></p>
        <p>Error Status: <span class="status" style="background: {health['error_color']}">{health['error_status']}</span></p>
        <p>Overall Status: <span class="status" style="background: {health['overall_color']}">{health['overall_status']}</span></p>
        <h3>Recent Errors</h3>
        {error_messages or '<p>No errors</p>'}
    </div>
    <a href="/"><button>Refresh</button></a>
</body>
</html>
"""

while True:
    try:
        try:
            conn, addr = server.accept()
            print("🔌 New connection from:", addr)
        except OSError as e:
            if e.errno == 11:  # EAGAIN
                time.sleep(0.1)
                continue
            error_log.append(f"OSError in accept: {str(e)}")
            if len(error_log) > 5:
                error_log.pop(0)
            raise

        # Read HTTP request
        buffer = bytearray(1024)
        try:
            length = conn.recv_into(buffer)
        except OSError as e:
            if e.errno == 11:  # EAGAIN
                time.sleep(0.1)
                conn.close()
                continue
            error_log.append(f"OSError in recv: {str(e)}")
            if len(error_log) > 5:
                error_log.pop(0)
            conn.close()
            continue

        response = html_page()
        conn.send(response.encode('utf-8'))
        conn.close()
    except Exception as e:
        print("⚠️ Server error:", e)
        error_log.append(f"Server error: {str(e)}")
        if len(error_log) > 5:
            error_log.pop(0)
        time.sleep(0.1)
