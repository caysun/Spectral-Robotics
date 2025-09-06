#include <DFRobot_AS7341.h>
DFRobot_AS7341 as7341;

void setup() {
  Serial.begin(115200);
  while (!Serial) {
    delay(1);
  }
  Serial.println("Setup Started");   
  if (as7341.begin() != 0){
    Serial.println("Could not find AS7341");
    while (1) delay(10);
  }

  Serial.println("Sensor found");

  //  //Integration time = (ATIME + 1) x (ASTEP + 1) x 2.78µs
  //  //Set the value of register ATIME(1-255), through which the value of Integration time can be calculated. The value represents the time that must be spent during data reading.
   as7341.setAtime(59);
  //  //Set the value of register ASTEP(0-65534), through which the value of Integration time can be calculated. The value represents the time that must be spent during data reading.
   as7341.setAstep(599);
  //  //Set gain value(0~10 corresponds to X0.5,X1,X2,X4,X8,X16,X32,X64,X128,X256,X512)
   as7341.setAGAIN(4);
  //  //Enable LED
   as7341.enableLed(true);
  //  //Set pin current to control brightness (1~20 corresponds to current 4mA,6mA,8mA,10mA,12mA,......,42mA)
   as7341.controlLed(20);
}

void loop() {
  // Turn LED on only when taking measurements
  as7341.enableLed(true);

  // Read all channels at the same time and store in as7341 object
  DFRobot_AS7341::sModeOneData_t data1;
  DFRobot_AS7341::sModeTwoData_t data2;

  as7341.startMeasure(as7341.eF1F4ClearNIR);
  data1 = as7341.readSpectralDataOne();

  as7341.startMeasure(as7341.eF5F8ClearNIR);
  data2 = as7341.readSpectralDataTwo();

  // as7341.enableLed(false);

  // Print tab-separated values for Serial Plotter
  /* Serial.print(data1.ADF1); Serial.print("\t");
  Serial.print(data1.ADF2); Serial.print("\t");
  Serial.print(data1.ADF3); Serial.print("\t");
  Serial.print(data1.ADF4); Serial.print("\t");
  Serial.print(data2.ADF5); Serial.print("\t");
  Serial.print(data2.ADF6); Serial.print("\t");
  Serial.print(data2.ADF7); Serial.print("\t");
  Serial.print(data2.ADF8); Serial.print("\t");
  Serial.print((data1.ADCLEAR + data2.ADCLEAR)/2); Serial.print("\t");
  Serial.println((data1.ADNIR + data2.ADNIR)/2); */

  // float clearAvg = ((float)data1.ADCLEAR + (float)data2.ADCLEAR)/2.0;
  // Serial.print("RATIO F1/CLR: "); Serial.println((float)data1.ADF1 / clearAvg);

  // Print out the stored values for each channel in a JSON format
  Serial.print("{");
  Serial.print("\"timestamp\": "); Serial.print(millis()); Serial.print(", ");
  Serial.print("\"spectral data\": {");
  Serial.print("\"F1\": "); Serial.print(data1.ADF1); Serial.print(", ");
  Serial.print("\"F2\": "); Serial.print(data1.ADF2); Serial.print(", ");
  Serial.print("\"F3\": "); Serial.print(data1.ADF3); Serial.print(", ");
  Serial.print("\"F4\": "); Serial.print(data1.ADF4); Serial.print(", ");
  Serial.print("\"F5\": "); Serial.print(data2.ADF5); Serial.print(", ");
  Serial.print("\"F6\": "); Serial.print(data2.ADF6); Serial.print(", ");
  Serial.print("\"F7\": "); Serial.print(data2.ADF7); Serial.print(", ");
  Serial.print("\"F8\": "); Serial.print(data2.ADF8); Serial.print(", ");
  Serial.print("\"Clear\": "); Serial.print((data1.ADCLEAR + data2.ADCLEAR)/2); Serial.print(", "); // Average value for now, change later if needed
  Serial.print("\"Near IR\": "); Serial.print((data1.ADNIR + data2.ADNIR)/2); // Average value for now, change later if needed
  Serial.print("}");
  Serial.println("}");

  delay(100);
}
