import wifi
import socketpool
import board
import digitalio
import gc
import time

# Wi-Fi credentials
SSID = "Aman_4g"
PASSWORD = "amansah17"

print("📶 Connecting to Wi-Fi...")
wifi.radio.connect(SSID, PASSWORD)
print("✅ Connected to", SSID)
print("🌐 IP Address:", wifi.radio.ipv4_address)

# LED Setup
main_led = digitalio.DigitalInOut(board.IO2)
main_led.direction = digitalio.Direction.OUTPUT
main_led.value = False

blue_led = digitalio.DigitalInOut(board.IO4)
blue_led.direction = digitalio.Direction.OUTPUT
blue_led.value = False

# Server setup
pool = socketpool.SocketPool(wifi.radio)
server = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
server.setsockopt(pool.SOL_SOCKET, pool.SO_REUSEADDR, 1)
server.bind((str(wifi.radio.ipv4_address), 85))
server.listen(1)

print(f"🌍 Server running at http://{wifi.radio.ipv4_address}:85")

# Runtime tracking
start_time = time.monotonic()
error_log = []

# Health checker
def get_system_health():
    wifi_status = "Connected" if wifi.radio.connected else "Disconnected"
    wifi_rssi = getattr(wifi.radio, 'rssi', None)
    wifi_signal = f"{wifi_rssi} dBm" if wifi_rssi is not None else "Unknown"

    free_mem = gc.mem_free()
    total_mem = 51200
    mem_percent = (free_mem / total_mem) * 100
    if mem_percent > 50:
        mem_health, mem_color = "Healthy", "green"
    elif mem_percent > 20:
        mem_health, mem_color = "Warning", "orange"
    else:
        mem_health, mem_color = "Critical", "red"

    uptime = time.monotonic() - start_time
    uptime_status = "Stable" if uptime > 60 else "Initializing"
    uptime_color = "green" if uptime > 60 else "blue"

    error_status = "No recent errors" if not error_log else f"{len(error_log)} recent error(s)"
    error_color = "green" if not error_log else "orange"

    overall_status = "System Healthy"
    overall_color = "green"
    if wifi_status == "Disconnected" or mem_health == "Critical" or error_log:
        overall_status, overall_color = "System Warning", "orange"

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

# HTML page generator
def html_page(page, main_led_state, blue_led_state):
    health = get_system_health()
    placeholder_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIA8eWrdwAAAABJRU5ErkJggg=="

    html_content = f"""HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html><head><title>ESP32 Web Server</title>
<style>
body {{ font-family: Arial; background: #f4f4f4; }}
.navbar {{ background-color: #333; overflow: hidden; }}
.navbar a {{ float: left; color: white; padding: 14px 20px; text-decoration: none; }}
.navbar a.active {{ background-color: #007bff; }}
.card {{ background: white; padding: 20px; margin: 20px; border-radius: 8px; }}
.status {{ padding: 10px; border-radius: 5px; }}
</style></head><body>
<div class="navbar">
<a href="/" class="{'active' if page=='home' else ''}">Home</a>
<a href="/about" class="{'active' if page=='about' else ''}">About</a>
<a href="/contact" class="{'active' if page=='contact' else ''}">Contact</a>
<a href="/control" class="{'active' if page=='control' else ''}">Control</a>
<a href="/dashboard" class="{'active' if page=='dashboard' else ''}">Dashboard</a>
</div><div class="content">
"""

    if page == "dashboard":
        html_content += f"""
<div class="card">
  <h2>📊 System Dashboard</h2>
  <p><strong>Overall Status:</strong> <span class="status" style="background:{health['overall_color']};">{health['overall_status']}</span></p>
  <p><strong>Wi-Fi Status:</strong> {health['wifi_status']} ({health['wifi_signal']})</p>
  <p><strong>Memory:</strong> {health['mem_health']} - {health['mem_percent']:.2f}% free <span style="color:{health['mem_color']};">●</span></p>
  <p><strong>Uptime:</strong> {int(health['uptime'])} sec - {health['uptime_status']} <span style="color:{health['uptime_color']};">●</span></p>
  <p><strong>Errors:</strong> {health['error_status']} <span style="color:{health['error_color']};">●</span></p>
</div>
"""

    elif page == "about":
        html_content += f"""
<div class="card"><h2>About</h2><p>This is an ESP32-based web server using CircuitPython.</p></div>"""

    elif page == "contact":
        html_content += f"""
<div class="card"><h2>Contact</h2><p>Email: example@domain.com<br>Phone: 1234567890</p></div>"""

    elif page == "control":
        html_content += f"""
<div class="card">
<h2>Main LED is {'ON' if main_led_state else 'OFF'}</h2>
<p><a href="/led/on"><button>Turn ON</button></a> <a href="/led/off"><button>Turn OFF</button></a></p>
<h2>Blue LED is {'ON' if blue_led_state else 'OFF'}</h2>
<p><a href="/blueled/on"><button>Turn ON</button></a> <a href="/blueled/off"><button>Turn OFF</button></a></p>
</div>"""

    else:
        html_content += f"""
<div class="card"><h2>Welcome</h2><p>This is a web server running on ESP32 using CircuitPython.</p></div>"""

    html_content += "</div></body></html>"
    return html_content

# Main loop
while True:
    try:
        conn, addr = server.accept()
        print("🔌 Connection from:", addr)
        buffer = bytearray(1024)
        length = conn.recv_into(buffer)
        request = buffer[:length].decode('utf-8')
        print("📥", request.split("\r\n")[0])

        page = "home"
        if "GET /about" in request:
            page = "about"
        elif "GET /contact" in request:
            page = "contact"
        elif "GET /control" in request:
            page = "control"
        elif "GET /dashboard" in request:
            page = "dashboard"
        elif "GET /led/on" in request:
            main_led.value = True
            page = "control"
        elif "GET /led/off" in request:
            main_led.value = False
            page = "control"
        elif "GET /blueled/on" in request:
            blue_led.value = True
            page = "control"
        elif "GET /blueled/off" in request:
            blue_led.value = False
            page = "control"

        response = html_page(page, main_led.value, blue_led.value)
        conn.send(response.encode('utf-8'))
        conn.close()

    except Exception as e:
        print("⚠️ Error:", e)
        error_log.append(str(e))
        if len(error_log) > 10:
            error_log.pop(0)

