# 🔌 Arduino Connection Guide

Complete setup guide for Arduino hardware integration with the helmet detection system.

## 📋 Required Components

### Hardware
- **Arduino Uno** (or compatible board)
- **5V Relay Module** (for motor control)
- **DC Motor** (12V recommended)
- **Red LED** (5mm)
- **220Ω Resistor** (for LED)
- **Buzzer** (5V active buzzer)
- **Breadboard** (optional, for testing)
- **Jumper Wires**
- **USB Cable** (Type A to Type B)

### Power Supply
- **12V Power Supply** (for motor)
- **5V Power Supply** (for Arduino, if not using USB)

## 🔧 Wiring Diagram

```
Arduino Uno Pinout:
┌─────────────────────────────────────┐
│                                     │
│  [USB]                              │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │                                 │ │
│  │  Pin 8  → Relay Module         │ │
│  │  Pin 9  → 220Ω → Red LED       │ │
│  │  Pin 11 → Buzzer               │ │
│  │  GND    → Common Ground        │ │
│  │  5V     → Relay VCC            │ │
│  │                                 │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘

Detailed Connections:
┌─────────────────────────────────────┐
│ Arduino Uno                         │
├─────────────────────────────────────┤
│ Pin 8  → Relay IN (Signal)         │
│ Pin 9  → 220Ω Resistor → LED (+)   │
│ Pin 11 → Buzzer (+)                │
│ GND    → LED (-), Buzzer (-)       │
│ 5V     → Relay VCC                 │
│ GND    → Relay GND                 │
└─────────────────────────────────────┘

Relay Module:
┌─────────────────────────────────────┐
│ Relay Module                        │
├─────────────────────────────────────┤
│ IN  → Arduino Pin 8                │
│ VCC → Arduino 5V                   │
│ GND → Arduino GND                  │
│ COM → 12V Power Supply (+)         │
│ NO  → Motor (+)                    │
│ NC  → Not Connected                │
└─────────────────────────────────────┘

Motor Circuit:
┌─────────────────────────────────────┐
│ 12V Power Supply                    │
├─────────────────────────────────────┤
│ (+) → Relay COM                    │
│ (-) → Motor (-)                    │
│ Relay NO → Motor (+)               │
└─────────────────────────────────────┘
```

## 🛠 Step-by-Step Setup

### Step 1: Prepare Components

1. **Gather all components**
   - Arduino Uno
   - Relay module
   - Motor
   - LED with resistor
   - Buzzer
   - Power supplies
   - Jumper wires

2. **Test components individually**
   - Test LED with battery
   - Test buzzer with 5V
   - Test relay with multimeter

### Step 2: Basic Arduino Test

1. **Connect Arduino to computer**
   - Use USB cable
   - Install Arduino drivers if needed

2. **Upload test code**
   ```cpp
   void setup() {
     Serial.begin(9600);
     pinMode(8, OUTPUT);
     pinMode(9, OUTPUT);
     pinMode(11, OUTPUT);
     Serial.println("Arduino Ready!");
   }
   
   void loop() {
     // Test LED
     digitalWrite(9, HIGH);
     delay(1000);
     digitalWrite(9, LOW);
     delay(1000);
   }
   ```

### Step 3: Connect LED

1. **LED Connection**
   ```
   Arduino Pin 9 → 220Ω Resistor → LED (+) → LED (-) → Arduino GND
   ```

2. **Test LED**
   - Upload the test code above
   - LED should blink every second

### Step 4: Connect Buzzer

1. **Buzzer Connection**
   ```
   Arduino Pin 11 → Buzzer (+) → Buzzer (-) → Arduino GND
   ```

2. **Test Buzzer**
   ```cpp
   void setup() {
     pinMode(11, OUTPUT);
   }
   
   void loop() {
     tone(11, 1000);  // 1kHz tone
     delay(500);
     noTone(11);
     delay(500);
   }
   ```

### Step 5: Connect Relay and Motor

1. **Relay Connection**
   ```
   Arduino Pin 8  → Relay IN
   Arduino 5V     → Relay VCC
   Arduino GND    → Relay GND
   ```

2. **Motor Connection**
   ```
   12V Power (+) → Relay COM
   12V Power (-) → Motor (-)
   Relay NO      → Motor (+)
   ```

3. **Test Motor**
   ```cpp
   void setup() {
     pinMode(8, OUTPUT);
   }
   
   void loop() {
     digitalWrite(8, LOW);   // Motor ON
     delay(2000);
     digitalWrite(8, HIGH);  // Motor OFF
     delay(2000);
   }
   ```

### Step 6: Upload Main Code

1. **Open Arduino IDE**
2. **Open `helmet_control_fixed.ino`**
3. **Select Board**: Tools → Board → Arduino Uno
4. **Select Port**: Tools → Port → COM5 (or your port)
5. **Click Upload**

## 🔍 Finding COM Port

### Windows
1. **Device Manager**
   - Press `Win + X` → Device Manager
   - Expand "Ports (COM & LPT)"
   - Look for "Arduino" or "USB Serial Device"
   - Note the COM port number

2. **Arduino IDE**
   - Tools → Port
   - Select the correct COM port

### Linux
```bash
ls /dev/ttyUSB*
ls /dev/ttyACM*
```

### macOS
```bash
ls /dev/tty.usbmodem*
ls /dev/tty.usbserial*
```

## ⚙️ Configuration

### Update COM Port in Python Script

1. **Open `helmet-detector/scripts/detect.py`**
2. **Find this line**:
   ```python
   arduino = serial.Serial('COM5', 9600, timeout=1)
   ```
3. **Change 'COM5' to your actual port**

### Test Arduino Communication

1. **Open Arduino Serial Monitor**
   - Tools → Serial Monitor
   - Set baud rate to 9600

2. **Send test signals**
   - Send '1' → Should activate motor, turn off LED/buzzer
   - Send '0' → Should deactivate motor, turn on LED/buzzer

## 🐛 Troubleshooting

### Arduino Not Detected
- **Check USB cable**
- **Install drivers**
- **Try different USB port**
- **Check Device Manager**

### LED Not Working
- **Check polarity** (LED has + and -)
- **Verify resistor connection**
- **Test with multimeter**
- **Check Pin 9 connection**

### Buzzer Not Working
- **Check polarity**
- **Verify Pin 11 connection**
- **Test with simple tone()**
- **Check if active/passive buzzer**

### Motor Not Responding
- **Check relay connections**
- **Verify 12V power supply**
- **Test relay with multimeter**
- **Check motor connections**

### Serial Communication Issues
- **Check baud rate (9600)**
- **Verify COM port**
- **Check USB connection**
- **Restart Arduino IDE**

## 📊 Signal Reference

| Signal | Action | Motor | LED | Buzzer |
|--------|--------|-------|-----|--------|
| '1' | Helmet Detected | ON | OFF | OFF |
| '0' | No Helmet | OFF | ON | Alert |

## 🔧 Advanced Configuration

### Custom Pin Assignment
```cpp
// Change these in helmet_control_fixed.ino
const int motorPin = 8;     // Motor control pin
const int ledPin = 9;       // LED control pin
const int buzzerPin = 11;   // Buzzer control pin
```

### Custom Alert Pattern
```cpp
// Modify buzzer alert in the code
for (int i = 0; i < 3; i++) {
  digitalWrite(buzzerPin, HIGH);
  delay(300);  // Beep duration
  digitalWrite(buzzerPin, LOW);
  delay(200);  // Pause between beeps
}
```

## ✅ Verification Checklist

- [ ] Arduino connects to computer
- [ ] LED blinks with test code
- [ ] Buzzer makes sound
- [ ] Relay clicks when activated
- [ ] Motor runs with relay
- [ ] Serial communication works
- [ ] Main code uploads successfully
- [ ] Python script finds correct COM port
- [ ] All components respond to signals

## 📞 Support

If you encounter issues:
1. Check all connections
2. Test components individually
3. Verify power supplies
4. Check Arduino serial monitor
5. Review troubleshooting section

---

**Happy building! 🔧⚡** 