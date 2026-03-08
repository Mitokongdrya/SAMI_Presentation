// Trigger Pin of Ultrasonic Sensor
#define TRIG_PINR 7
#define TRIG_PINL 8
#define TRIG_PINM 9

// Echo Pin of Ultrasonic Sensor, must be on an interrupt pin!
#define ECHO_PINR 4
#define ECHO_PINL 5
#define ECHO_PINM 6

// RFID reader pins
//#define RFID_INTER 2  // This is the same as echo interr1
// the PN532 SCK, MOSI, and MISO pins need to be connected to the Arduino's
// hardware SPI SCK, MOSI, and MISO pins.  On an Arduino Uno these are
// SCK = 13, MOSI = 11, MISO = 12.  The SS line can be any digital IO pin.
#define PN532_SCK 13
#define PN532_MISO 12
#define PN532_MOSI 11
#define PN532_SS  10
//#define PN532_IRQ A4
#define RFID_TRIG A5


#define ECHO_INTERR1 2
#define ECHO_INTERR2 3

//PIR sensor input pin
#define PIR_PINR  A1
#define PIR_PINL  A0

//Push button input pin
#define BTN_1 A2
#define BTN_2 A3
#define BTN_3 A4


#define NUM_READINGS 10  // Number of readings to average.
#define THRESHOLD    50   // Deviation threshold from the average (in centimeters).

#define DEBUG 0       // if we want to get debug messages
#define DEBUG_ULTRA 0 // if we want to debug just the ultrasonic bits
#define DEBUG_PIR 0   // if we want to debug just the pir bits
#define DEBUG_RFID 0  // if we want to debug just the rfid bits
#define DEBUG_BTN 0   // if we want to debug just the button bits
#define DEBUG_LOGIC 1 // if we want to debug just the logic bits

volatile bool cardTriggered = false; // Did the card detector get triggered??
bool cardCurrentState = false; // Is there currently a card?
bool haveRFIDReader = false; // Did we connect to the card reader?

// Constants
const unsigned int MAX_DIST = 23200;
const unsigned long ALARM_DURATION_MS = 1000;
const unsigned long DETECTION_PERIOD_MS = 5000; // 5 seconds
const unsigned long ULTRASONIC_INTERVAL_MS = 100; // Interval between ultrasonic measurements
