#ifndef SENSORS_H
#define SENSORS_H

#include <Arduino.h>

// Sensor pin definitions
#ifndef IR_SENSOR_LEFT
#define IR_SENSOR_LEFT 2
#endif
#ifndef IR_SENSOR_RIGHT
#define IR_SENSOR_RIGHT 3
#endif
#ifndef ULTRASONIC_TRIG
#define ULTRASONIC_TRIG 7
#endif
#ifndef ULTRASONIC_ECHO
#define ULTRASONIC_ECHO 8
#endif

// Sensor data structure
struct SensorData {
  int leftIR;
  int rightIR;
  float distance;      // in centimeters
  float temperature;   // onboard / ambient reading or estimated
  float humidity;      // ambient reading or estimated
};

inline void initializeSensors() {
  pinMode(IR_SENSOR_LEFT, INPUT);
  pinMode(IR_SENSOR_RIGHT, INPUT);
  pinMode(ULTRASONIC_TRIG, OUTPUT);
  pinMode(ULTRASONIC_ECHO, INPUT);
  digitalWrite(ULTRASONIC_TRIG, LOW);
}

inline SensorData readSensors() {
  SensorData data;
  data.temperature = 24.5; // Nominal ambient temperature
  data.humidity = 45.0;    // Nominal relative humidity

  // Read digital IR proximity / line sensors (0 = obstacle / line detected, 1 = clear)
  data.leftIR = digitalRead(IR_SENSOR_LEFT);
  data.rightIR = digitalRead(IR_SENSOR_RIGHT);

  // Trigger ultrasonic sensor pulse
  digitalWrite(ULTRASONIC_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(ULTRASONIC_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(ULTRASONIC_TRIG, LOW);

  // Wait for echo pulse with a 30ms timeout (~500 cm max range)
  long duration = pulseIn(ULTRASONIC_ECHO, HIGH, 30000);
  if (duration <= 0) {
    // Out of range or timeout -> default safe distance
    data.distance = 400.0;
  } else {
    data.distance = (duration * 0.0343) / 2.0;  // Speed of sound = 343 m/s = 0.0343 cm/us
    if (data.distance < 2.0 || data.distance > 400.0) {
      data.distance = 400.0;
    }
  }

  return data;
}

#endif // SENSORS_H
