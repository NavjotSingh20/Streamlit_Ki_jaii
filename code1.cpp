int count = 0, l, r;
int flag = 0;
long st = millis(), endt;
int trigPin = 13;
int echoPin = 12;
int prevGantry = 0;  // Tracks last detected gantry (replaces prevPulseState)

void setup() {
  Serial.begin(9600);
  pinMode(A0, INPUT); // Left IR sensor
  pinMode(A1, INPUT); // Right IR sensor
  pinMode(A2, INPUT); // Gantry IR receiver input
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(5, OUTPUT); // Left motor forward
  pinMode(6, OUTPUT); // Left motor reverse
  pinMode(8, OUTPUT); // Right motor forward
  pinMode(7, OUTPUT); // Right motor reverse
}

void forward() {
  digitalWrite(5, HIGH);
  digitalWrite(6, LOW);
  digitalWrite(8, HIGH);
  digitalWrite(7, LOW);
}

void left() {
  digitalWrite(8, LOW);
  digitalWrite(6, LOW);
  digitalWrite(5, HIGH);
  digitalWrite(7, LOW);
}

void right() {
  digitalWrite(8, HIGH);
  digitalWrite(6, LOW);
  digitalWrite(5, LOW);
  digitalWrite(7, LOW);
}

void stopMotors() {
  digitalWrite(5, LOW);
  digitalWrite(6, LOW);
  digitalWrite(8, LOW);
  digitalWrite(7, LOW);
}

int getDistance() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  long duration = pulseIn(echoPin, HIGH, 20000); // 20ms timeout
  int distance = duration * 0.0343 / 2;
  return distance;
}

void loop() {
  if (Serial.available() > 0 && Serial.read() == 'y') {
    flag = 1;
  }

  if (flag == 1) {

    // -------- GANTRY DETECTION (pulse-width based, from second code) --------
    int g = pulseIn(A2, HIGH, 5000); // Read pulse width from IR receiver on A2

    if (g >= 500 && g < 1000 && prevGantry != 1) {
      Serial.println("Gantry 1 detected");
      stopMotors();
      delay(1000);
      prevGantry = 1;
    }
    else if (g >= 1000 && g < 2000 && prevGantry != 2) {
      Serial.println("Gantry 2 detected");
      stopMotors();
      delay(1000);
      prevGantry = 2;
    }
    else if (g >= 2000 && g < 3000 && prevGantry != 3) {
      Serial.println("Gantry 3 detected");
      stopMotors();
      delay(1000);
      prevGantry = 3;
    }

    // -------- OBSTACLE DETECTION --------
    int distance = getDistance();
    if (distance > 0 && distance <= 20) {
      Serial.print("Obstacle at ");
      Serial.print(distance);
      Serial.println(" cm. Stopping.");
      stopMotors();
      delay(2000);
      return;
    }

    // -------- IR LINE FOLLOWING --------
    l = digitalRead(A0);
    r = digitalRead(A1);

    if (l == 1 && r == 1) forward();
    else if (l == 0 && r == 1) left();
    else if (l == 1 && r == 0) right();
    else if (l == 0 && r == 0) {
      endt = millis();
      if (endt - st > 1000) {
        count++;
        st = millis();
      }
      switch (count) {
        case 1:
        case 3:
        case 4:
        case 6:
          Serial.print("Forward: ");
          Serial.println(count);
          forward();
          break;
        case 2:
          Serial.print("RIGHT Turn: ");
          Serial.println(count);
          right();
          delay(500);
          break;
        case 5:
          Serial.print("Right Turn: ");
          Serial.println(count);
          right();
          delay(300);
          break;

        case 7:
          Serial.print("Forward: ");
          Serial.println(count);
          forward();
          delay(300);
          break;

        default:
          stopMotors();
          Serial.println("Stopped");
          flag = 0;
          break;
      }
    }
  }
}
