import wifi
import socketpool
import time
import board
import digitalio

# Set up built-in LED (GPIO2 usually)
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
led.value = False  # Start with LED OFF

# Connect to Wi-Fi
wifi.radio.connect("Aman_4g", "amansah17")
print("Connected to WiFi")
print("IP address:", wifi.radio.ipv4_address)

# Create a simple socket server
pool = socketpool.SocketPool(wifi.radio)
server = pool.socket()
server.bind(('0.0.0.0', 80))
server.listen(1)

# HTML for the control page
def webpage():
    led_status = "ON" if led.value else "OFF"
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ESP32 LED Control</title>
        <style>
            body {{ font-family: Arial; text-align: center; background: #f0f0f0; }}
            .button {{ padding: 20px; font-size: 20px; margin: 20px; border: none; border-radius: 10px; cursor: pointer; }}
            .on {{ background-color: green; color: white; }}
            .off {{ background-color: red; color: white; }}
        </style>
    </head>
    <body>
        <h1>ESP32 LED Control Portal</h1>
        <p>LED is currently <strong>{led_status}</strong></p>
        <a href="/led/on"><button class="button on">Turn ON</button></a>
        <a href="/led/off"><button class="button off">Turn OFF</button></a>
    </body>
    </html>
    """

# Main loop
while True:
    conn, addr = server.accept()
    print("Connection from", addr)
    request = conn.recv(1024)
    request = str(request)

    if "/led/on" in request:
        led.value = True
    elif "/led/off" in request:
        led.value = False

    # Send HTTP response
    response = webpage()
    conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
    conn.send(response)
    conn.close()
