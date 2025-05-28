import wifi
import socketpool
import board
import digitalio

SSID = "enter_wifi_SSID"
PASSWORD = "enter_password"

print("📶 Connecting to Wi-Fi...")
wifi.radio.connect(SSID, PASSWORD)
print("✅ Connected to", SSID)
print("🌐 IP Address:", wifi.radio.ipv4_address)

# Main LED setup
main_led = digitalio.DigitalInOut(board.IO2)  # Change to board.LED or correct pin
main_led.direction = digitalio.Direction.OUTPUT
main_led.value = False

# Blue LED setup
blue_led = digitalio.DigitalInOut(board.IO4)  # Adjust to the correct pin for Blue LED
blue_led.direction = digitalio.Direction.OUTPUT
blue_led.value = False

pool = socketpool.SocketPool(wifi.radio)
server = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
server.setsockopt(pool.SOL_SOCKET, pool.SO_REUSEADDR, 1)
server.bind((str(wifi.radio.ipv4_address), 80))
server.listen(1)

print(f"🌍 Server running at http://{wifi.radio.ipv4_address}:80")

def html_page(page, main_led_state, blue_led_state):
    # Base64-encoded placeholder image (tiny 1x1 pixel image to keep response lightweight)
    placeholder_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIA8eWrdwAAAABJRU5ErkJggg=="
    
    # HTML content with navigation bar and page-specific content
    html_content = f"""HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESP32 Web Server</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
        }}
        .navbar {{
            background-color: #333;
            overflow: hidden;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        .navbar a {{
            float: left;
            display: block;
            color: white;
            text-align: center;
            padding: 14px 20px;
            text-decoration: none;
            transition: background-color 0.3s;
        }}
        .navbar a:hover {{
            background-color: #555;
        }}
        .navbar a.active {{
            background-color: #007bff;
        }}
        .navbar .menu-icon {{
            display: none;
            float: right;
            padding: 14px 20px;
            cursor: pointer;
        }}
        .content {{
            padding: 20px;
            max-width: 800px;
            margin: auto;
        }}
        .card {{
            background: white;
            padding: 20px;
            margin: 10px 0;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 5px;
        }}
        button {{
            padding: 10px 20px;
            margin: 10px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
        }}
        button:hover {{
            background-color: #0056b3;
        }}
        @media screen and (max-width: 600px) {{
            .navbar a:not(.menu-icon) {{
                display: none;
            }}
            .navbar.responsive a {{
                float: none;
                display: block;
                text-align: left;
            }}
            .navbar .menu-icon {{
                display: block;
            }}
        }}
    </style>
</head>
<body>
    <div class="navbar" id="navbar">
        <a href="/" class="{'active' if page == 'home' else ''}">Home</a>
        <a href="/about" class="{'active' if page == 'about' else ''}">About</a>
        <a href="/contact" class="{'active' if page == 'contact' else ''}">Contact</a>
        <a href="/control" class="{'active' if page == 'control' else ''}">Control</a>
        <a href="/dashboard" class="{'active' if page == 'dashboard' else ''}">Dashboard</a>
        <a href="javascript:void(0);" class="menu-icon" onclick="toggleMenu()">☰</a>
    </div>
    <div class="content">
"""

    # Page-specific content
    if page == "about":
        html_content += f"""
        <div class="card">
            <h2>About This Project</h2>
            <img src="{placeholder_image}" alt="Project Image" style="width:200px;height:200px;background:#ccc;">
            <p>This is an ESP32-based web server project built with CircuitPython. It allows remote control of devices and displays information through a web interface.</p>
        </div>
"""
    elif page == "contact":
        html_content += f"""
        <div class="card">
            <h2>Contact Us</h2>
            <img src="{placeholder_image}" alt="Contact Image" style="width:200px;height:200px;background:#aaa;">
            <p>Email: example@domain.com</p>
            <p>Phone: (123) 456-7890</p>
            <p>Address: 123 Tech Street, IoT City</p>
        </div>
"""
    elif page == "control":
        html_content += f"""
        <div class="card">
            <h1>Main LED is {'ON' if main_led_state else 'OFF'}</h1>
            <p><a href="/led/on"><button>Turn Main LED ON</button></a></p>
            <p><a href="/led/off"><button>Turn Main LED OFF</button></a></p>
            <h1>Blue LED is {'ON' if blue_led_state else 'OFF'}</h1>
            <p><a href="/blueled/on"><button>Turn Blue LED ON</button></a></p>
            <p><a href="/blueled/off"><button>Turn Blue LED OFF</button></a></p>
        </div>
"""
    elif page == "dashboard":
        html_content += f"""
        <div class="card">
            <h2>Dashboard</h2>
            <img src="{placeholder_image}" alt="Dashboard Image" style="width:200px;height:200px;background:#ddd;">
            <p>System Status: Operational</p>
            <p>IP Address: {wifi.radio.ipv4_address}</p>
            <p>Uptime: Not tracked</p>
        </div>
"""
    else:  # Home page
        html_content += f"""
        <div class="card">
            <h2>Welcome to ESP32 Web Server</h2>
            <img src="{placeholder_image}" alt="Home Image" style="width:200px;height:200px;background:#eee;">
            <p>This is a home automation server running on an ESP32 with CircuitPython. Navigate to other pages to explore features.</p>
        </div>
"""

    # Close HTML with JavaScript for navbar toggle
    html_content += """
    </div>
    <script>
        function toggleMenu() {
            var navbar = document.getElementById("navbar");
            if (navbar.className === "navbar") {
                navbar.className += " responsive";
            } else {
                navbar.className = "navbar";
            }
        }
    </script>
</body>
</html>
"""
    return html_content

while True:
    try:
        conn, addr = server.accept()
        print("🔌 New connection from:", addr)
        
        # Read HTTP request
        buffer = bytearray(1024)
        length = conn.recv_into(buffer)
        request = buffer[:length].decode('utf-8')
        print("📥 Request:", request.split("\r\n")[0])
        
        # Determine page and handle LED control
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
        
        # Send response
        response = html_page(page, main_led.value, blue_led.value)
        conn.send(response.encode('utf-8'))
        
        conn.close()
    except Exception as e:
        print("⚠️ Server error:", e)
