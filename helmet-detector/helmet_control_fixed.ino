/*
 * Helmet Detection Arduino Controller - FIXED VERSION
 * Simplified and reliable code for helmet detection
 * 
 * Wiring:
 * - Motor: Pin 8 (via relay) - simulates bike engine
 * - Red LED: Pin 9 (with 220Ω resistor)
 * - Buzzer: Pin 10 (direct connection) - for alerts
 */

const int motorPin = 8;     // Motor control pin (via relay)
const int ledPin = 9;       // Red LED control pin
const int buzzerPin = 11;   // Buzzer control pin (direct)

void setup() {
  pinMode(motorPin, OUTPUT);
  pinMode(ledPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);
  Serial.begin(9600);
  
  // Initialize everything OFF
  digitalWrite(motorPin, HIGH); // Relay OFF (active LOW)
  digitalWrite(ledPin, LOW);    // LED OFF
  digitalWrite(buzzerPin, LOW); // Buzzer OFF
  
  Serial.println("=== Helmet Detection Arduino Ready ===");
  Serial.println("Waiting for signals (1=helmet, 0=no helmet)...");
}

void loop() {
  if (Serial.available() > 0) {
    char data = Serial.read();
    
    Serial.print("Received: ");
    Serial.println(data);
    
    if (data == '1') {
      // Helmet detected: Motor ON, LED OFF, Buzzer OFF
      Serial.println("HELMET DETECTED - Starting bike engine");
      
      digitalWrite(ledPin, LOW);     // LED OFF
      digitalWrite(buzzerPin, LOW);  // Buzzer OFF
      digitalWrite(motorPin, LOW);   // Motor ON (relay activated)
      
      Serial.println("Status: Motor running, LED off, Buzzer off");
      
    } else if (data == '0') {
      // No helmet: Motor OFF, LED ON, Buzzer ON
      Serial.println("NO HELMET - Stopping bike and alerting");
      
      digitalWrite(motorPin, HIGH);  // Motor OFF (relay deactivated)
      digitalWrite(ledPin, HIGH);    // LED ON
      
      // Buzzer alert - multiple beeps
      Serial.println("Buzzer alert starting...");
      for (int i = 0; i < 3; i++) {
        digitalWrite(buzzerPin, HIGH);
        delay(300);
        digitalWrite(buzzerPin, LOW);
        delay(200);
        Serial.print("Beep ");
        Serial.println(i + 1);
      }
      
      Serial.println("Status: Motor stopped, LED on, Buzzer alerted");
      
    } else {
      // Invalid data
      Serial.print("Invalid signal: ");
      Serial.println(data);
    }
    
    Serial.println("Ready for next signal...");
  }
} 