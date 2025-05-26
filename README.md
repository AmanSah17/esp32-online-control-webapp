# ESP32 Web Control Panel

A lightweight web-based control panel for ESP32 devices that provides a user-friendly interface for controlling onboard LED and managing contact form submissions.

## Features

- **Real-time LED Control**: Toggle the onboard LED (GPIO2) through a web interface
- **Contact Form**: Submit and store messages locally on the ESP32
- **Responsive Design**: Mobile-friendly interface that works on all devices
- **Local Storage**: Messages are stored in JSON format on the ESP32's filesystem
- **Simple Setup**: Easy configuration with WiFi credentials

## Hardware Requirements

- ESP32 development board
- USB cable for programming
- WiFi network access

## Software Requirements

- CircuitPython installed on ESP32
- Required CircuitPython libraries:
  - `board`
  - `digitalio`
  - `wifi`
  - `socketpool`

## Installation

1. Install CircuitPython on your ESP32
2. Copy the required libraries to your ESP32's `lib` folder
3. Copy `webservice.py` to your ESP32's root directory
4. Update the WiFi credentials in the code:
   ```python
   SSID = "Your_WiFi_Name"
   PASSWORD = "Your_WiFi_Password"
   ```

## Usage

1. Power on your ESP32
2. The device will automatically:
   - Connect to the specified WiFi network
   - Start the web server
   - Print the IP address to the serial console
3. Open a web browser and navigate to the ESP32's IP address
4. Use the interface to:
   - Control the onboard LED
   - Submit contact form messages
   - View system information

## Interface Sections

### Home
- Welcome message
- Basic system information

### Control
- LED status indicator
- ON/OFF toggle buttons

### About
- System description
- Features overview

### Contact
- Contact form with fields for:
  - Name
  - Email
  - Message

## File Structure

```
contacts/              # Directory for stored messages
  ├── contact_*.json  # Individual message files
webservice.py         # Main application file
```

## Message Storage

- Messages are stored in the `contacts` directory
- Each message is saved as a JSON file
- Filenames include timestamps for easy tracking
- Maximum storage limited by ESP32's filesystem (typically 10MB)

## Error Handling

The system includes error handling for:
- WiFi connection failures
- LED setup issues
- Server initialization problems
- Form submission errors
- File system operations

## Security Considerations

- The web interface is only accessible on the local network
- No external internet access required
- Data is stored locally on the ESP32
- Basic form validation implemented

## Limitations

- Single client connection at a time
- Limited storage capacity
- Basic error handling
- No SSL/TLS encryption

## Troubleshooting

1. **WiFi Connection Issues**
   - Verify WiFi credentials
   - Check WiFi signal strength
   - Ensure ESP32 is in range

2. **LED Control Not Working**
   - Verify GPIO2 connection
   - Check for hardware damage
   - Restart the ESP32

3. **Form Submission Fails**
   - Check available storage space
   - Verify filesystem permissions
   - Check serial console for error messages

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.

## Author

Created by Mr.Aman Sah
Automation and RnD Engineer
Email : amansah1717@gmail.com
