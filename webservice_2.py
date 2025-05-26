import time
import board
import digitalio
import wifi
import socketpool
import json
import os

# --- Configuration ---
SSID = "network_4g"        # Replace with your Wi-Fi name
PASSWORD = "XXX7XXXXX"  # Replace with your Wi-Fi password

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
    <title>ESP32 Control Panel</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .navbar {{
            background: #2c3e50;
            padding: 1rem;
            position: fixed;
            width: 100%;
            top: 0;
            z-index: 1000;
        }}
        .navbar a {{
            color: white;
            text-decoration: none;
            margin: 0 15px;
            font-weight: 500;
        }}
        .navbar a:hover {{
            color: #3498db;
        }}
        .container {{
            max-width: 1200px;
            margin: 80px auto 0;
            padding: 20px;
        }}
        .section {{
            margin: 40px 0;
            padding: 20px;
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .button {{
            padding: 12px 24px;
            font-size: 16px;
            margin: 10px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        .on {{ background-color: #2ecc71; color: white; }}
        .off {{ background-color: #e74c3c; color: white; }}
        .button:hover {{ opacity: 0.9; transform: scale(1.05); }}
        .form-group {{
            margin: 15px 0;
        }}
        input, textarea {{
            width: 100%;
            padding: 8px;
            margin: 5px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .footer {{
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 20px;
            margin-top: 40px;
        }}
        h1, h2 {{ color: #2c3e50; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="#home">Home</a>
        <a href="#about">About</a>
        <a href="#control">Control</a>
        <a href="#contact">Contact</a>
    </nav>

    <div class="container">
        <section id="home" class="section">
            <h1>ESP32 Control Panel</h1>
            <p>Welcome to your ESP32 control interface. This system allows you to control various aspects of your ESP32 device.</p>
        </section>

        <section id="control" class="section">
            <h2>LED Control</h2>
            <p>LED is currently <strong>{status}</strong></p>
            <a href="/led/on"><button class="button on">Turn ON</button></a>
            <a href="/led/off"><button class="button off">Turn OFF</button></a>
        </section>

        <section id="about" class="section">
            <h2>About</h2>
            <p>This is an ESP32-based control system that provides a web interface for controlling various aspects of your device. The system runs on a local server and can be accessed through any device connected to the same network.</p>
        </section>

        <section id="contact" class="section">
            <h2>Contact Form</h2>
            <form action="/submit" method="POST">
                <div class="form-group">
                    <label for="name">Name:</label>
                    <input type="text" id="name" name="name" required>
                </div>
                <div class="form-group">
                    <label for="email">Email:</label>
                    <input type="email" id="email" name="email" required>
                </div>
                <div class="form-group">
                    <label for="message">Message:</label>
                    <textarea id="message" name="message" rows="4" required></textarea>
                </div>
                <button type="submit" class="button on">Submit</button>
            </form>
        </section>
    </div>

    <footer class="footer">
        <p>&copy; 2024 ESP32 Control Panel. All rights reserved.</p>
    </footer>
</body>
</html>"""

# --- Handle Form Submission ---
def save_contact_data(data):
    try:
        # Create a contacts directory if it doesn't exist
        if not os.path.exists('contacts'):
            os.makedirs('contacts')
        
        # Generate filename based on timestamp
        filename = f'contacts/contact_{int(time.time())}.json'
        
        # Save the data
        with open(filename, 'w') as f:
            json.dump(data, f)
        return True
    except Exception as e:
        print("Error saving contact data:", e)
        return False

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
        elif "/submit" in request and "POST" in request:
            # Extract form data from POST request
            content_length = int(request.split("Content-Length: ")[1].split("\r\n")[0])
            form_data = request.split("\r\n\r\n")[1][:content_length]
            
            # Parse form data
            data = {}
            for item in form_data.split('&'):
                key, value = item.split('=')
                data[key] = value
            
            # Save the data
            if save_contact_data(data):
                response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nForm submitted successfully!"
            else:
                response = "HTTP/1.1 500 Internal Server Error\r\nContent-Type: text/plain\r\n\r\nError saving form data"
            conn.send(response.encode())
            conn.close()
            continue

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
