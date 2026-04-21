#include <NewPing.h>

// --- Flags and constants ---
bool start = false;
const int trigPin = 13;
const int echoPin = 12;
const int maxDistance = 20;
NewPing sonar(trigPin, echoPin, maxDistance);

int distanceCm;
int counter = 0;
int prevGantry = 0;

unsigned long prevTime;
unsigned long currentTime;

// --- Setup ---
void setup() {
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(7, OUTPUT);
  pinMode(8, OUTPUT);
  pinMode(A0, INPUT);
  pinMode(A1, INPUT);
  pinMode(4, INPUT);

  Serial.begin(9600);

  prevTime = millis();   
}

// --- Motor control ---
void Forward()  { digitalWrite(5,HIGH); digitalWrite(6,LOW);  digitalWrite(7,LOW);  digitalWrite(8,HIGH); }
void Backward() { digitalWrite(5,LOW);  digitalWrite(6,HIGH); digitalWrite(7,HIGH); digitalWrite(8,LOW);  }
void Left()     { digitalWrite(5,HIGH); digitalWrite(6,LOW);  digitalWrite(7,LOW);  digitalWrite(8,LOW);  }
void Right()    { digitalWrite(5,LOW);  digitalWrite(6,LOW);  digitalWrite(7,LOW);  digitalWrite(8,HIGH); }
void Stop()     { digitalWrite(5,LOW);  digitalWrite(6,LOW);  digitalWrite(7,LOW);  digitalWrite(8,LOW);  }

// --- Main loop ---
void loop() {

  if (Serial.available()) {
    if (Serial.read() == 'x') start = true;
  }

  if (start) {
    int d0 = digitalRead(A0);
    int d1 = digitalRead(A1);

    // --- Gantry detection ---
    int g = pulseIn(4, HIGH, 5000);

    if (g >= 500 && g < 1000 && prevGantry != 1) {
      Serial.println("gantry 111");
      Stop();
      delay(500);                     
      prevGantry = 1;
    }
    else if (g >= 1000 && g < 2000 && prevGantry != 2) {
      Serial.println("gantry 222");
      Stop();
      delay(500);
      prevGantry = 2;
    }
    else if (g >= 2000 && g < 3000 && prevGantry != 3) {
      Serial.println("gantry 333");
      Stop();
      delay(500);
      prevGantry = 3;
    }

    // --- Parking sequence ---
    if (d0 == 0 && d1 == 0) {

      currentTime = millis();

      switch (counter) {

        case 0:
          if (currentTime - prevTime > 500) {
            prevTime = currentTime;
            Forward(); delay(25);
            counter++;
          }
          break;

        case 1:
          if (currentTime - prevTime > 750) {
            prevTime = currentTime;
            Left(); delay(20);
            counter++;
          }
          break;

        case 2:
          if (currentTime - prevTime > 1000) {
            prevTime = currentTime;
            Forward(); delay(13);
            counter++;
          }
          break;

        case 3:
          if (currentTime - prevTime > 1000) {
            prevTime = currentTime;
            Left(); delay(150);
            counter++;
          }
          break;

        case 4:
          if (currentTime - prevTime > 500) {
            prevTime = currentTime;
            Forward(); delay(10);
            counter++;
          }
          break;

        case 5:
          Forward();
          delay(200);
          Left();
          delay(1200);
          counter++;   
          break;

        case 6:
          if (currentTime - prevTime > 500) {
            Stop();
            Serial.println("Buggy Parked");
            start = false;
          }
          break;
      }

      Serial.print("Counter: ");
      Serial.println(counter);
    }

    else if (d0 == 0) {
      Left();
    }
    else if (d1 == 0) {
      Right();
    }
    else {
      Forward();
    }
  }

  // --- Obstacle detection ---
  int d = sonar.ping_cm();   

  if (d > 0 && d < 15) {
    Stop();
    Serial.println("Obstacle detected, waiting...");

    while (true) {
      int d2 = sonar.ping_cm();
      if (!(d2 > 0 && d2 < 15)) break;
      delay(100);
    }
  }
}
