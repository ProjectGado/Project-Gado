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
#define ACTUATOR_START 25

const String handshake = "Im a robot!";

const String firmware_version = "0.9.2";
const String hardware_version = "2.5";

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
  // format: [VALUE]c 
  // where VALUE is an int and c is a command
  // list of commands:
  // s -> move actuator (requires VALUE)
  // a -> move arm (requires VALUE)
  // v -> control vacuum (requires VALUE)
  // d -> echoes location information
  // l -> lower and lift (does not turn on vacuum)
  // L -> upgraded lower and lift (turns on vacuum at the end)
  // h -> handshake (returns "Im a robot!")
  // p -> drop (drops until the sensor clicks)
  // ? -> returns hardware and firmware version info
  
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
        pumpSettings(v);
        v = 0;
        break;
      case 'd':
        gatherAndEcho();
        break;
      case 'l':
        lowerAndLift();
        break;
      case 'L':
        advancedLowerAndLift();
        break;
      case 'h':
        Serial.print(handshake);  
        break;
      case 'p':
        drop();
        break;
      case '?':
        echoAbout();
        break;
      default:
        // invalid command?
        // resetting value just in case
        v = 0;
        break;
    }
  }  
}

void pumpSettings(int v) {
    if (v > 0) {
      digitalWrite(pump_standy, HIGH);
      analogWrite(pump_pwm,v);
    } else {
      digitalWrite(pump_standy, LOW);
      analogWrite(pump_pwm,v);
    }
    pump_level = v;
}

void gatherAndEcho() {
   gatherSensorData();
   echoDataJson();
}
void gatherSensorData() {
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
    //Button state
    Serial.print("\"button_state\": \"" + String(lastButtonState) + "\"");
    Serial.print("}");
    Serial.println();
}

void echoAbout()
{
    Serial.print("{");
    Serial.print("\"hardware_version\": \"" + String(arm_pos) + "\"");
    Serial.print(",");
    Serial.print("\"firmware_version\": \"" + String(firmware_version) + "\"");
    Serial.print("}");
    Serial.println();
}

void advancedLowerAndLift()
{
  // The big difference is that it drops, then turns on the vacuum
  // then it lifts. Standard procedure was vacuum, drop, then lift.
  drop();
  pumpSettings(255);
  analogWrite(actuator_pin, ACTUATOR_START);
  actuator_pos = ACTUATOR_START;
}

void drop()
{
  int v = actuator_pos;
  int last_p = analogRead(actuator_position_pin);
  int curr_p = last_p;
  int start_p = curr_p;
  int diff = last_p - curr_p;
    
  while(1)
  {
    // take a current button reading
    // sometimes this pretends to have a button press
    // so we need to record when we noticed a click
    // then we're going to come back to check to make
    // sure that we had another click
    int reading = analogRead(buttonPin);

    // record only when a change of state occurs
    if(reading != lastButtonState) {
      lastDebounceTime = millis();
    }
    
    // If it isn't coming up as clicked, then let's think
    // about moving the arm further down
    if (reading == 0)
    {
      // get the current reading of the actuator's position
      // this is an analog value that doesn't precisely correspond with ANYTHING
      curr_p = analogRead(actuator_position_pin);
      
      // how much did it change from the last time we changed v?
      // (the values decrease as its lowered)
      diff = start_p - curr_p; // this should be positive
      
      // if it's dropped by 3, then we're probably good
      // if it stopped dropping, then we're also probably good
      // (by good, I mean we are go for lowering it further)
      if((diff >= 3) || (curr_p == last_p))
      {
        // drop it one
        v = v + 1;
        
        // did we reach the bottom?
        if (v > 255) {
          break; // abandon ship!
        }
        
        // tell it to drop, record where it dropped to
        // and record this as a new start
        analogWrite(actuator_pin, v); // drop it
        actuator_pos = v; // record where we're going
        start_p = curr_p; // record where we're at
      }
      
      // update last position and wait a moment
      last_p = curr_p;
      delay(10);
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
