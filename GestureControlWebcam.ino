#define LED1 2   // Thumb
#define LED2 4   // Index
#define LED3 5   // Middle
#define LED4 18  // Ring
#define LED5 19  // Pinky
#define BUZZER 21

int lastBuzzerState = -1;

void setup() {
  Serial.begin(115200);

  pinMode(LED1, OUTPUT);
  pinMode(LED2, OUTPUT);
  pinMode(LED3, OUTPUT);
  pinMode(LED4, OUTPUT);
  pinMode(LED5, OUTPUT);
  pinMode(BUZZER, OUTPUT);
}

void setFingerLEDs(bool thumb, bool index, bool middle, bool ring, bool pinky) {
  digitalWrite(LED1, thumb ? HIGH : LOW);
  digitalWrite(LED2, index ? HIGH : LOW);
  digitalWrite(LED3, middle ? HIGH : LOW);
  digitalWrite(LED4, ring ? HIGH : LOW);
  digitalWrite(LED5, pinky ? HIGH : LOW);
}

void setBuzzer(int state) {
  if (state != lastBuzzerState) {
    digitalWrite(BUZZER, state ? HIGH : LOW);
    lastBuzzerState = state;
  }
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');

    // Right hand LEDs: send 5-character string like "10101" (Thumb→Pinky)
    if (cmd.startsWith("L")) {
      if (cmd.length() >= 6) {
        bool t = cmd[1] == '1';
        bool i = cmd[2] == '1';
        bool m = cmd[3] == '1';
        bool r = cmd[4] == '1';
        bool p = cmd[5] == '1';
        setFingerLEDs(t, i, m, r, p);
      }
    }
    // Left hand buzzer
    else if (cmd.startsWith("B")) {
      int state = cmd.substring(1).toInt();
      setBuzzer(state);
    }
  }
}
