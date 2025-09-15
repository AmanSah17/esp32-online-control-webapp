import wifi
import socketpool
import board
import digitalio
import time

# ---------- Wi-Fi Setup ----------
SSID = "SSID"
PASSWORD = "PASSWORD"

print("Connecting to Wi-Fi...")
wifi.radio.connect(SSID, PASSWORD)
print("Connected! IP:", wifi.radio.ipv4_address)

# ---------- LED Setup ----------
led = digitalio.DigitalInOut(board.IO13)  # LED connected to GPIO13
led.direction = digitalio.Direction.OUTPUT

# ---------- Socket Server ----------
pool = socketpool.SocketPool(wifi.radio)
server = pool.socket()
server.bind(("0.0.0.0", 80))
server.listen(1)

print("HTTP server ready! Open:", wifi.radio.ipv4_address)

# ---------- Control Flag ----------
led_running = False
last_toggle_time = time.monotonic()
state = False  # LED state

while True:
    # --- Handle incoming requests ---
    try:
        conn, addr = server.accept()
        buffer = bytearray(1024)
        bytes_read = conn.recv_into(buffer)
        request = buffer[:bytes_read].decode("utf-8")

        print("New connection from", addr)
        print("Request:", request)

        if "GET /led/on" in request:
            led_running = True
            response_body = "LED loop started"
        elif "GET /led/off" in request:
            led_running = False
            led.value = False  # turn off immediately
            response_body = "LED loop stopped"
        else:
            response_body = "ESP32 Web Server Running"

        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{response_body}"
        conn.send(response.encode("utf-8"))
        conn.close()

    except Exception as e:
        pass  # ignore socket errors

    # --- Run LED loop if enabled ---
    if led_running:
        now = time.monotonic()
        if state and now - last_toggle_time >= 10:
            # After 10s ON → turn OFF
            led.value = False
            state = False
            last_toggle_time = now
        elif not state and now - last_toggle_time >= 2:
            # After 2s OFF → turn ON
            led.value = True
            state = True
            last_toggle_time = now






