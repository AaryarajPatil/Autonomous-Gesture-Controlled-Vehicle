#ifndef MOTORS_H
#define MOTORS_H

#include <Arduino.h>

// Default motor pin definitions (can be overridden if defined prior)
#ifndef MOTOR_LEFT_FWD
#define MOTOR_LEFT_FWD 5
#endif
#ifndef MOTOR_LEFT_BWD
#define MOTOR_LEFT_BWD 6
#endif
#ifndef MOTOR_RIGHT_FWD
#define MOTOR_RIGHT_FWD 9
#endif
#ifndef MOTOR_RIGHT_BWD
#define MOTOR_RIGHT_BWD 10
#endif
#ifndef MOTOR_ENABLE
#define MOTOR_ENABLE 4
#endif

inline void initializeMotors() {
  pinMode(MOTOR_LEFT_FWD, OUTPUT);
  pinMode(MOTOR_LEFT_BWD, OUTPUT);
  pinMode(MOTOR_RIGHT_FWD, OUTPUT);
  pinMode(MOTOR_RIGHT_BWD, OUTPUT);
  pinMode(MOTOR_ENABLE, OUTPUT);
  digitalWrite(MOTOR_ENABLE, HIGH);
}

// Motor control functions using if-else chain (C++ String compatibility)
inline void moveCar(const String& direction, int speed) {
  speed = constrain(speed, 0, 255);  // Ensure speed is within valid PWM range

  if (direction == "FORWARD") {
    analogWrite(MOTOR_LEFT_FWD, speed);
    analogWrite(MOTOR_LEFT_BWD, 0);
    analogWrite(MOTOR_RIGHT_FWD, speed);
    analogWrite(MOTOR_RIGHT_BWD, 0);
  } else if (direction == "BACKWARD") {
    analogWrite(MOTOR_LEFT_FWD, 0);
    analogWrite(MOTOR_LEFT_BWD, speed);
    analogWrite(MOTOR_RIGHT_FWD, 0);
    analogWrite(MOTOR_RIGHT_BWD, speed);
  } else if (direction == "LEFT") {
    // Spin left: left wheels backward, right wheels forward
    analogWrite(MOTOR_LEFT_FWD, 0);
    analogWrite(MOTOR_LEFT_BWD, speed);
    analogWrite(MOTOR_RIGHT_FWD, speed);
    analogWrite(MOTOR_RIGHT_BWD, 0);
  } else if (direction == "RIGHT") {
    // Spin right: left wheels forward, right wheels backward
    analogWrite(MOTOR_LEFT_FWD, speed);
    analogWrite(MOTOR_LEFT_BWD, 0);
    analogWrite(MOTOR_RIGHT_FWD, 0);
    analogWrite(MOTOR_RIGHT_BWD, speed);
  } else {
    // Default STOP
    analogWrite(MOTOR_LEFT_FWD, 0);
    analogWrite(MOTOR_LEFT_BWD, 0);
    analogWrite(MOTOR_RIGHT_FWD, 0);
    analogWrite(MOTOR_RIGHT_BWD, 0);
  }
}

inline void stopCar() {
  analogWrite(MOTOR_LEFT_FWD, 0);
  analogWrite(MOTOR_LEFT_BWD, 0);
  analogWrite(MOTOR_RIGHT_FWD, 0);
  analogWrite(MOTOR_RIGHT_BWD, 0);
}

#endif // MOTORS_H
