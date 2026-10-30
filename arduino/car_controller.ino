#include "motors.h"
#include "sensors.h"
#include "communication.h"

// Serial Communication configuration
const unsigned long BAUD_RATE = 9600;
unsigned long lastTelemetryTime = 0;
const unsigned long TELEMETRY_INTERVAL_MS = 100; // 10 Hz telemetry loop

void setup() {
  Serial.begin(BAUD_RATE);
  initializeMotors();
  initializeSensors();
  stopCar();
  Serial.println("SYSTEM_READY");
}

void processCommand(String command) {
  command.trim();
  if (command.length() == 0) return;

  // Handle MOVE or CONTROL command
  // Format: MOVE:<DIR>:<SPEED_0_255> or CONTROL:<DIR>:<SPEED_0.0_1.0>
  if (command.startsWith("MOVE:") || command.startsWith("CONTROL:")) {
    int firstColon = command.indexOf(':');
    int secondColon = command.indexOf(':', firstColon + 1);

    if (firstColon != -1 && secondColon != -1) {
      String direction = command.substring(firstColon + 1, secondColon);
      direction.toUpperCase();
      String speedStr = command.substring(secondColon + 1);

      int pwmSpeed = 0;
      if (command.startsWith("CONTROL:")) {
        // float 0.0 to 1.0 -> map to 0 to 255
        float normSpeed = speedStr.toFloat();
        pwmSpeed = (int)(constrain(normSpeed, 0.0f, 1.0f) * 255.0f);
      } else {
        // integer 0 to 255
        pwmSpeed = speedStr.toInt();
      }

      moveCar(direction, pwmSpeed);
      sendAck(direction);
    }
  } else if (command == "STOP" || command == "EMERGENCY_STOP") {
    stopCar();
    sendAck("STOP");
  } else if (command == "SENSOR_REQUEST") {
    SensorData sensorData = readSensors();
    sendSensorData(sensorData);
  } else if (command == "PING") {
    Serial.println("PONG");
  } else if (command == "RESET") {
    stopCar();
    sendAck("RESET");
  }
}

void loop() {
  // Check for serial commands
  while (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    processCommand(command);
  }

  // Periodic telemetry streaming
  unsigned long now = millis();
  if (now - lastTelemetryTime >= TELEMETRY_INTERVAL_MS) {
    lastTelemetryTime = now;
    SensorData sensorData = readSensors();
    sendSensorData(sensorData);
  }

  delay(10);
}
