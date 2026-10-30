#ifndef COMMUNICATION_H
#define COMMUNICATION_H

#include <Arduino.h>
#include "sensors.h"

// Sends telemetry matching both formats: SENSOR_DATA:distance:temperature:humidity
// and SENSORS:leftIR,rightIR,distance for backward compatibility
inline void sendSensorData(const SensorData& data) {
  Serial.print("SENSOR_DATA:");
  Serial.print(data.distance, 2);
  Serial.print(":");
  Serial.print(data.temperature, 1);
  Serial.print(":");
  Serial.println(data.humidity, 1);
}

inline void sendSensorDataVerbose(const SensorData& data) {
  Serial.print("SENSORS:");
  Serial.print(data.leftIR);
  Serial.print(",");
  Serial.print(data.rightIR);
  Serial.print(",");
  Serial.println(data.distance, 2);
}

inline void sendAck(const String& cmd) {
  Serial.print("ACK:");
  Serial.println(cmd);
}

#endif // COMMUNICATION_H
