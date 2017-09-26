/*
    Using reference for fast PWM from http://r6500.blogspot.my/2014/12/fast-pwm-on-arduino-leonardo.html
    Using reference for fast GPIO from https://github.com/pololu/fastgpio-arduino
*/

// #include <Servo.h>

// Servo steering;

#include <FastGPIO.h>

uint8_t  steerPin = 9;
uint8_t  motorPin = 10;
uint8_t  togglePin = 11;

volatile int16_t  throttleVal;
volatile int8_t  steerVal;
String modeVal;
String receivedArs[2];
String receivedString;
String receivedArr[2];

volatile int8_t mapsteerVal;
volatile int8_t mapthrottleVal;


// Setting for Fast PWM
#define throtlefreq 5   // 11719 Hz (~12kHz) using using Timer4 for Motor Driver
#define servofreq   5   // 61 Hz using Timer1 for servo


#define throttlepin OCR4D // (Pin D6) using output compare (OC) method @low level PWM 
#define servopin    OCR1B // (Pin D10) using output compare (OC) method @low level PWM


// convert duty (0..100) to PWM (0..255)
#define DUTY2PWM(x)   ((255*(x))/100)

// macro convert degree (0..180) to PWM (0..255)
#define DEG2PWM(x)    ((255*(x))/180)


// configure PWM clock for servo
void pwm_clock_servo(int mode){
//    TCCR1A configuration
  TCCR1A = 1;

  // TCCR1B configuration
  // clock mode &  fast pwm
  TCCR1B = mode | 0x08;

  // TCCR1C Configuration
  TCCR1C = 0;
}

// set PWM to pin D9
void pwmsetservo(int value){
  OCR1B = value;  // set PWM Value
  DDRB |= 1<<6;   // set output mode B6 (OC)
  TCCR1A |= 0x20;  // activate the pwm
} 


// configure PWM clock for throttle
void pwm_clock_throttle(int mode){
//    TCCR4A configuration
  TCCR4A = 0;

  // TCCR4B configuration
  TCCR4B = mode;

  // TCCR4C Configuration
  TCCR4C = 0;

  // TCCR4D Configuration
  TCCR4D = 0;

  // TCCR4D Configuration
  TCCR4D = 0;

  /*
    PLL Configuration
    Use 96MHz / 2 = 48MHz
  */
  PLLFRQ=(PLLFRQ&0xCF)|0x30;

  // Terminal cout for Timer 4 PMW
  OCR4C = 255;
}

// set PWM to pin D6
void pwmsetthrottle(int value){
  OCR4D = value;    // set PWM Value
  DDRD |= 1<<7;     // set output mode D7 (OC)
  TCCR4C |= 0x09;   // activate the pwm
} 



// set gpio using fast gpio module --> pin 5 = D5
void motordirlow() __attribute__((noinline));
void motordirlow(){
  FastGPIO::Pin<5>::setOutputLow();
}


void motordirhigh() __attribute__((noinline));
void motordirhigh(){
  FastGPIO::Pin<5>::setOutputHigh();
}

void motordirtoggle() __attribute__((noinline));
void motordirtoggle(){
  FastGPIO::Pin<5>::setOutputToggle();
}


void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  // pinMode(steerPin, OUTPUT);
  // pinMode(motorPin, OUTPUT);
  // pinMode(togglePin, OUTPUT);
  // steering.attach(steerPin);
  // steering.write(23);

  motordirlow();

  pwm_clock_servo(servofreq);
  pwm_clock_throttle(throtlefreq);

  pwmsetservo(DEG2PWM(23));
  pwmsetthrottle(DUTY2PWM(50));
  delay(1000);

}

volatile int value = 0;

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0)
  {
    receivedString = Serial.readStringUntil('\n');
    int com1index = receivedString.indexOf(',');
    int com2index = receivedString.indexOf(',', com1index + 1);
    receivedArr[0] = receivedString.substring(0,com1index);
    receivedArr[1] = receivedString.substring(com1index + 1, com2index);
    receivedArr[2] = receivedString.substring(com2index + 1);
    steerVal = receivedArr[2].toInt();
    throttleVal = receivedArr[1].toInt();
    modeVal = receivedArr[0];
  }
  mapsteerVal = map(steerVal,-100,100,0,46);
  mapthrottleVal = DUTY2PWM(throttleVal);
    // steering.write(mapsteerVal);
  pwmsetservo(mapsteerVal);
  throttle(togglePin, motorPin, throttleVal, mapthrottleVal);


  // value = (value + 10 )%256;
  // pwmsetservo(value);
  // pwmsetthrottle(value);

  // motordirtoggle();

  // delay(2000);
}


void throttle(uint8_t togglePin, uint8_t motorPin, int8_t realthrottleVal, uint8_t unrealthrottleVal)
{
  if (realthrottleVal < 0)
    {
      // digitalWrite(togglePin, HIGH);
      motordirhigh();
    }
  else
  {
      // digitalWrite(togglePin, LOW);
    motordirlow();
  }
  // analogWrite(motorPin, unrealthrottleVal);
  pwmsetthrottle(unrealthrottleVal);
}
