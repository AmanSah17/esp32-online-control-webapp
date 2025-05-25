import time
import board
import digitalio
import wifi
import socketpool

# --- Configuration ---
SSID = "Aman_4g"        # Replace with your Wi-Fi name
PASSWORD = "amansah17"  # Replace with your Wi-Fi password

# --- Setup onboard LED (GPIO2 on most ESP32 boards) ---
try:
    led = digitalio.DigitalInOut(board.IO2)
    led.direction = digitalio.Direction.OUTPUT
    led.value = False
except Exception as e:
    print("LED setup failed:", e)

# --- Connect to Wi-Fi ---
try:
    wifi.radio.connect(SSID, PASSWORD)
    print("✅ Connected to WiFi")
    print("🌐 IP address:", wifi.radio.ipv4_address)
except Exception as e:
    print("❌ Failed to connect to Wi-Fi:", e)
    while True:
        pass  # Stop execution

# --- Setup Socket Server ---
try:
    pool = socketpool.SocketPool(wifi.radio)
    server = pool.socket()
    server.bind(('0.0.0.0', 80))
    server.listen(1)
    print("🌍 HTTP server started, waiting for connections...")
except Exception as e:
    print("❌ Server setup failed:", e)
    while True:
        pass

# --- HTML Response Page ---
def webpage():
    status = "ON" if led.value else "OFF"
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>ESP32 LED Control</title>
    <style>
        body {{ font-family: Arial; text-align: center; background: #eef; }}
        .button {{ padding: 20px; font-size: 20px; margin: 20px; border-radius: 10px; cursor: pointer; }}
        .on {{ background-color: green; color: white; }}
        .off {{ background-color: red; color: white; }}
    </style>
</head>
<body>
    <h1>ESP32 LED Control</h1>
    <p>LED is currently <strong>{status}</strong></p>
    <a href="/led/on"><button class="button on">Turn ON</button></a>
    <a href="/led/off"><button class="button off">Turn OFF</button></a>
</body>
</html>"""

# --- Main Server Loop ---
while True:
    try:
        conn, addr = server.accept()
        print(f"\n🔌 Connection from {addr}")

        buffer = bytearray(1024)
        bytes_read = conn.recv_into(buffer)
        request = str(buffer[:bytes_read], "utf-8")
        print("📥 Request:", request)

        # Handle routes
        if "/led/on" in request:
            led.value = True
        elif "/led/off" in request:
            led.value = False

        # Send response
        html = webpage()
        conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
        conn.send(html)
        conn.close()

    except Exception as e:
        print("⚠️ Error during request:", e)
        try:
            conn.close()
        except:
            pass

