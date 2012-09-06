#include <Servo.h> 

//Declare variables
Servo arm; 
int arm_pos = 1344;
int actuator_pos = 25;
int arm_first_limit = 0;
int arm_second_limit = 180;
int actuator_first_limit = 25;
int actuator_second_limit = 255;
int arm_delay = 5;
int pump_level = 0;
int act_pos_sense;
int light_value = 0;
int fsr_value;
int last_level;
int pump_current;
int servo_min = 2000;
int servo_max = 1350;
double photo_change_ratio = .60;
double version = 2.0;
int y = 0;

//bumper settings
long lastDebounceTime = 0;
long debounceDelay = 50;
int buttonState;
int lastButtonState = LOW;

//Declare pins
int actuator_pin = 6;
int pump_in_1 = 7;
int pump_in_2 = 8;
int pump_standy = 4;
int pump_pwm = 3;
int current_sense_pin = 3;
int fsr_pin = 0;
int photo_sense_pin = 1;
int actuator_position_pin = 2;
int arm_servo_pin = 5;

#define buttonPin A1
#define ACTUATOR_START 30

const String handshake = "Im a robot!";

void setup() 
{ 
  //Initialize serial control
  Serial.begin(115200);
  
  //Move the actuator to the starting position
  analogWrite(actuator_pin, ACTUATOR_START);
  
  //Initilalize the arm servo
  pinMode(arm_servo_pin, OUTPUT);
  arm.attach(arm_servo_pin, servo_min, servo_max);
  
  //Initialize pump; for a diaphragm pump, these values don't really matter
  pinMode(pump_in_1, OUTPUT);
  pinMode(pump_in_2, OUTPUT);
  pinMode(pump_standy, OUTPUT);
  
  //Turn off standby power
  digitalWrite(pump_standy, LOW);
  
  //Set orientation settings
  digitalWrite(pump_in_1, HIGH);
  digitalWrite(pump_in_2, LOW);
  
  //Shut off the pump
  analogWrite(pump_pwm, 0);  
  
  //Map degrees to whatever the servo uses
  y = map(0, 0, 180, servo_min, servo_max);
  arm.writeMicroseconds(y);
} 
 
 
void loop() 
{ 
  static int v = 0;
  if ( Serial.available()) {
    char ch = Serial.read();
    switch(ch) {
      case '0'...'9':
        v = v * 10 + ch - '0';
        break;
      case 's':
        analogWrite(actuator_pin,v);
        actuator_pos = v;
        v = 0;
        break;
      case 'a':
        y = map(v, 0, 180, servo_min, servo_max);
        arm.writeMicroseconds(y);
        arm_pos = v;
        v = 0;
        break;
      case 'v':
        if (v > 0) {
            digitalWrite(pump_standy, HIGH);
            analogWrite(pump_pwm,v);
        } else {
            digitalWrite(pump_standy, LOW);
            analogWrite(pump_pwm,v);
        }
        pump_level = v;
        v = 0;
        break;
      case 'd':
        gatherAndEcho();
        break;  
      case 'L':
        printLightVsPositionData();
        break;
      case 'l':
        lowerAndLift();
        break;
      case 'h':
        Serial.print(handshake);  
        break;
      case 'p':
        drop();
        break;
    }
    if (ch != 'h' && ch != 'd' && ch != '0' && ch != '1' && ch != '2' && ch != '3' && ch != '4' && ch != '5' && ch != '6' && ch != '7' && ch != '8' && ch != '9' && ch != '\n' && ch != '\r') {
        gatherAndEcho();
    }
    }

    
} 

void gatherAndEcho() {
   gatherSensorData();
   echoDataJson();
}
void gatherSensorData() {
    //pump_current = analogRead(current_sense_pin);
    pump_current = getAveragedPumpCurrent();
    light_value = analogRead(photo_sense_pin);
    act_pos_sense = analogRead(actuator_position_pin);
    fsr_value = analogRead(fsr_pin);
    lastButtonState = analogRead(buttonPin);
}

//Print the robot's current state over the serial, in JSON
void echoDataJson() {
    Serial.print("{");
    //Arm position
    Serial.print("\"arm_pos\": \"" + String(arm_pos) + "\"");
    Serial.print(",");
    //Actuator position (desired)
    Serial.print("\"actuator_pos_d\": \"" + String(actuator_pos) + "\"");
    Serial.print(",");
    //Actuator position (sensed)
    Serial.print("\"actuator_pos_s\": \"" + String(act_pos_sense) + "\"");
    Serial.print(",");
    //Pump level
    Serial.print("\"pump_level\": \"" + String(pump_level) + "\"");
    Serial.print(",");
    //Light level
    Serial.print("\"light_value\": \"" + String(light_value) + "\"");
    Serial.print(",");
    //FSR value
    Serial.print("\"fsr_value\": \"" + String(fsr_value) + "\"");
    Serial.print(",");
    //Last level
    Serial.print("\"last_level\": \"" + String(last_level) + "\"");
    Serial.print(",");
    //Pump current
    Serial.print("\"pump_current\": \"" + String(pump_current) + "\"");
    Serial.print(",");
    //Button state
    Serial.print("\"button_state\": \"" + String(lastButtonState) + "\"");
    Serial.print("}");
    Serial.println();
}

void gotoLevelSense() {

}

void drop()
{
  int v = actuator_pos;
  int last_actuator_position = analogRead(actuator_position_pin);
  int current_actuator_position = last_actuator_position;
  
  while(1)
  {
    int reading = analogRead(buttonPin);
    
    if(reading != lastButtonState)
    {
      lastDebounceTime = millis();
    }
    
    //if ((millis() - lastDebounceTime) > debounceDelay)
    //{
    //buttonState = reading;
    
    if (reading == 0)
    {
      //get the current reading of the actuator's position
      current_actuator_position = analogRead(actuator_position_pin);
      
      //Serial.println("New act pos: " + v);
      if(current_actuator_position == last_actuator_position)
      {
        v = v + 10;
        
        analogWrite(actuator_pin, v);
        actuator_pos = v;
      }
      
      last_actuator_position = current_actuator_position;
      
      delay(50);
    }
    else if(reading > 0 && ((millis() - lastDebounceTime) > debounceDelay))
    {
      //spin forever
      Serial.println("STOPPP!");
      break;
    }
    //}
    lastButtonState = reading;
  }
}

void lowerAndLift()
{
  int v = actuator_pos;
  int last_actuator_position = analogRead(actuator_position_pin);
  int current_actuator_position = last_actuator_position;
  
  while(1)
  {
    int reading = analogRead(buttonPin);
    
    if(reading != lastButtonState)
    {
      lastDebounceTime = millis();
    }
    
    //if ((millis() - lastDebounceTime) > debounceDelay)
    //{
    //buttonState = reading;
    
    if (reading == 0)
    {
      //get the current reading of the actuator's position
      current_actuator_position = analogRead(actuator_position_pin);
      
      //Serial.println("New act pos: " + v);
      if(current_actuator_position == last_actuator_position)
      {
        v = v + 10;
        
        analogWrite(actuator_pin, v);
        actuator_pos = v;
      }
      
      last_actuator_position = current_actuator_position;
      
      delay(50);
    }
    else if(reading > 0 && ((millis() - lastDebounceTime) > debounceDelay))
    {
      //spin forever
      Serial.println("STOPPP!");
      analogWrite(actuator_pin, ACTUATOR_START);
      actuator_pos = ACTUATOR_START;
      break;
    }
    //}
    lastButtonState = reading;
  }
}
/*
//Drops the Z axis to pick up an item
void lowerAndLift() {
  int j = analogRead(photo_sense_pin);
  double i = double(analogRead(photo_sense_pin)) / double(j);
  while (i > photo_change_ratio) {
        actuator_pos += 10;
        analogWrite(actuator_pin, actuator_pos);
        delay(500);
        //Serial.println(i);
        i = double(analogRead(photo_sense_pin)) / double(j);
    }
  last_level = actuator_pos;
}
*/

//Calibration function
void printLightVsPositionData() {
  Serial.println("light, position");
  actuator_pos = 25;
  delay(5000);
  while (actuator_pos < 160) {
      analogWrite(actuator_pin, actuator_pos);
      delay(300);
      light_value = analogRead(photo_sense_pin);
      Serial.print(light_value);
      Serial.print(",");
      Serial.println(actuator_pos);
      actuator_pos += 1;
  }
}

//Smooth out the pump current reading through averaging
int getAveragedPumpCurrent() {
  int total = 0;
  int datapoints = 0;
  int last = analogRead(current_sense_pin);
  for(int i = 0; i<10; i+=1) {
    int value = analogRead(current_sense_pin);
    //Serial.println(abs(value - last));
    if (abs(value - last) < 5) {
      datapoints += 1;
      total += value;
      last = value;
    }
    delay(10);
  }
  return int(total/datapoints);
}
