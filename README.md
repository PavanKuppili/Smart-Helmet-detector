# 🪖 Helmet Detection System

An AI-powered helmet detection system using YOLOv8 for safety compliance monitoring with Arduino hardware integration.

## 🚀 Features

- **AI-Powered Detection**: YOLOv8-based helmet detection with high accuracy
- **Real-time Processing**: Live webcam detection with instant results
- **Hardware Integration**: Arduino control for motor, LED, and buzzer
- **Safety Compliance**: Automatic safety checks with hardware responses

## 📁 Project Structure

```
demo-helmate/
├── helmet-detector/
│   ├── data/
│   │   ├── data.yaml              # Dataset configuration
│   │   ├── train/                 # Training images (3,648)
│   │   ├── valid/                 # Validation images (372)
│   │   └── test/                  # Test images (149)
│   ├── models/
│   │   └── helmet.pt              # Trained YOLOv8 model (6.2MB)
│   ├── scripts/
│   │   └── detect.py              # Main detection script
│   ├── input/                     # Test images
│   └── helmet_control_fixed.ino   # Arduino code
├── yolov8n.pt                     # Base YOLOv8 model
├── requirements.txt               # Python dependencies
└── README.md                     # This file
```

## 🛠 Installation

### Prerequisites

- Python 3.8+
- Arduino IDE
- Webcam (for live detection)

### Setup

1. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify installation**
   ```bash
   python -c "import ultralytics, torch, cv2; print('✅ All dependencies installed')"
   ```

## 🎯 Usage

### Quick Start

1. **Test with a single image**
   ```bash
   cd helmet-detector
   python scripts/detect.py input/helmate-on-1.webp
   ```

2. **Start live webcam detection**
   ```bash
   python scripts/detect.py --webcam
   ```

### Detection Results

- **✅ PASS**: Helmet detected → Motor ON, LED OFF, Buzzer OFF
- **❌ FAIL**: No helmet → Motor OFF, LED ON, Buzzer alert
- **⚠️ CONFLICT**: Conflicting detections → Treat as FAIL
- **❓ NO_DETECTION**: No objects detected → Treat as FAIL

## 🔌 Arduino Setup

### Hardware Components

- **Arduino Uno** (or compatible)
- **Motor** (via relay) - simulates bike engine
- **Red LED** (with 220Ω resistor) - warning indicator
- **Buzzer** - alert system
- **USB Cable** - for serial communication

### Wiring Diagram

```
Arduino Uno:
├── Pin 8 → Relay → Motor (Engine control)
├── Pin 9 → 220Ω Resistor → Red LED (Warning light)
├── Pin 11 → Buzzer (Alert system)
└── USB → Computer (Serial Communication)
```

### Connection Steps

1. **Connect Hardware**
   - Connect motor to Pin 8 via relay module
   - Connect red LED to Pin 9 with 220Ω resistor
   - Connect buzzer to Pin 11
   - Connect Arduino to computer via USB

2. **Upload Arduino Code**
   - Open Arduino IDE
   - Open `helmet-detector/helmet_control_fixed.ino`
   - Select correct board and port
   - Click Upload

3. **Find COM Port**
   - Open Device Manager (Windows)
   - Look for "Arduino" under "Ports (COM & LPT)"
   - Note the COM port number (e.g., COM5)

4. **Update COM Port in Script**
   - Open `helmet-detector/scripts/detect.py`
   - Find line with `serial.Serial('COM5', 9600, timeout=1)`
   - Change 'COM5' to your actual COM port

### Arduino Code Overview

```cpp
// Pin definitions
const int motorPin = 8;     // Motor control
const int ledPin = 9;       // Red LED
const int buzzerPin = 11;   // Buzzer

// Signal handling
if (data == '1') {
    // Helmet detected: Motor ON, LED OFF, Buzzer OFF
    digitalWrite(motorPin, LOW);   // Motor ON
    digitalWrite(ledPin, LOW);     // LED OFF
    digitalWrite(buzzerPin, LOW);  // Buzzer OFF
} else if (data == '0') {
    // No helmet: Motor OFF, LED ON, Buzzer ON
    digitalWrite(motorPin, HIGH);  // Motor OFF
    digitalWrite(ledPin, HIGH);    // LED ON
    // Buzzer alert sequence
}
```

## 📊 Model Performance

### Dataset Statistics
- **Training Images**: 3,648
- **Validation Images**: 372
- **Test Images**: 149
- **Classes**: 2 (With Helmet, Without Helmet)

### Test Results
- **Helmet Detection**: 97.7% confidence
- **No Helmet Detection**: 88.4% confidence
- **Average Inference Time**: ~200ms per image

## 🔧 Configuration

### Model Parameters
- **Confidence Threshold**: 0.5
- **Camera Resolution**: 640x480
- **Detection Classes**: With Helmet, Without Helmet

### Arduino Settings
- **Baud Rate**: 9600
- **Timeout**: 1 second
- **Port**: COM5 (configurable)

## 🐛 Troubleshooting

### Common Issues

1. **Camera not detected**
   - Close other applications using camera
   - Try different camera indices (0, 1, 2)
   - Check camera drivers

2. **Arduino connection failed**
   - Check COM port in Device Manager
   - Update Arduino drivers
   - Try different COM ports (COM3, COM4, COM5, COM6)
   - Ensure Arduino code is uploaded

3. **Low detection accuracy**
   - Ensure good lighting
   - Position 2-3 feet from camera
   - Avoid shadows on face
   - Check image quality

4. **Model loading error**
   - Verify `helmet.pt` exists in `models/` folder
   - Check file permissions
   - Reinstall ultralytics if needed

### Arduino Troubleshooting

1. **Motor not responding**
   - Check relay connections
   - Verify Pin 8 connection
   - Test relay with multimeter

2. **LED not lighting**
   - Check 220Ω resistor connection
   - Verify Pin 9 connection
   - Test LED polarity

3. **Buzzer not working**
   - Check Pin 11 connection
   - Verify buzzer polarity
   - Test with simple tone() function

## 📝 Usage Examples

### Image Detection
```bash
# Test helmet detection
python scripts/detect.py input/helmate-on-1.webp

# Test no helmet
python scripts/detect.py input/helmate-off-1.jpg
```

### Live Detection
```bash
# Start webcam detection
python scripts/detect.py --webcam
```

### Expected Output
```
============================================================
HELMET DETECTION TEST RESULTS
============================================================
Total detections found: 1
🟢 With Helmet detected (confidence: 0.98)
Result: ✅ Helmet worn correctly

FINAL TEST RESULT
🎯 ✅ HELMET WORN CORRECTLY
   Safety compliance: PASSED ✅
   Status: SAFE TO PROCEED
```

## ⚠️ Safety Notice

This system is designed for educational and demonstration purposes. Always follow local safety regulations and wear appropriate protective equipment.

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Verify all connections
3. Test components individually
4. Check Arduino serial monitor for debugging

---

**Happy detecting! 🪖✨** 