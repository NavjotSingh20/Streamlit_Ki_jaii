#include <NewPing.h>

const int trigPin = 13;
const int echoPin = 12;
const int pin = 4;

long duration;
int distanceCm;

long st = 0;
int count = 0;
int flag = 0;

// ---------------- SETUP ----------------
void setup() {
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  for (int i = 5; i < 9; i++) {
    pinMode(i, OUTPUT);
  }

  pinMode(A2, INPUT);
  pinMode(A3, INPUT);
  pinMode(pin, INPUT);

  Serial.begin(9600);

  st = millis();
}

// ---------------- MOTOR ----------------
void stopp() {
  digitalWrite(5, LOW);
  digitalWrite(8, LOW);
  digitalWrite(6, LOW);
  digitalWrite(7, LOW);
}

void forward() {
  digitalWrite(5, HIGH);
  digitalWrite(8, HIGH);
  digitalWrite(6, LOW);
  digitalWrite(7, LOW);
}

void left() {
  digitalWrite(6, LOW);
  digitalWrite(7, LOW);
  digitalWrite(5, HIGH);
  digitalWrite(8, LOW);
}

void right() {
  digitalWrite(6, LOW);
  digitalWrite(7, LOW);
  digitalWrite(5, LOW);
  digitalWrite(8, HIGH);
}

// ---------------- LOOP ----------------
void loop() {

  // ---------------- GANTRY (RANGE + STABLE) ----------------
  static unsigned long lastTriggerTime = 0;

  int g = pulseIn(pin, HIGH, 5000);  // read pulse width

  if (millis() - lastTriggerTime > 300) {

    if (g >= 500 && g < 1000) {
      Serial.println("Gantry 1 detected");
      stopp();
      delay(800);
      lastTriggerTime = millis();
    }
    else if (g >= 1000 && g < 2000) {
      Serial.println("Gantry 2 detected");
      stopp();
      delay(800);
      lastTriggerTime = millis();
    }
    else if (g >= 2000 && g < 3000) {
      Serial.println("Gantry 3 detected");
      stopp();
      delay(800);
      lastTriggerTime = millis();
    }
  }

  // ---------------- START CONDITION ----------------
  if ((Serial.available() && Serial.read() == 'K') || flag == 1) {

    flag = 1;

    // ---------------- ULTRASONIC ----------------
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);

    duration = pulseIn(echoPin, HIGH, 20000);

    if (duration == 0)
      distanceCm = 999;
    else
      distanceCm = (duration * 0.034) / 2;

    if (distanceCm > 10) {

      int r = digitalRead(A2);
      int l = digitalRead(A3);

      // ---------------- LINE FOLLOW ----------------
      if (l == 1 && r == 1)
        forward();

      else if (l == 1 && r == 0)
        right();

      else if (l == 0 && r == 1)
        left();

      // ---------------- JUNCTION ----------------
      else if (l == 0 && r == 0) {

        delay(20);
        if (digitalRead(A2) == 0 && digitalRead(A3) == 0) {

          long endt = millis();

          if (endt - st > 600) {
            count++;
            Serial.print("Count = ");
            Serial.println(count);
            st = millis();
          }

          // ---------------- PATH ----------------
          if (count == 1) forward();
          else if (count == 2) { right(); delay(150); }
          else if (count == 3) forward();
          else if (count == 4) forward();
          else if (count == 5) { right(); delay(650); }

          // ---------------- FINAL STOP ----------------
          else if (count >= 6) {
            stopp();
            flag = 0;
          }
        }
      }
    }
    else {
      stopp();
    }
  }
}