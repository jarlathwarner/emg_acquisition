#if defined(ARDUINO) && ARDUINO >= 100
#include "Arduino.h"
#else
#include "WProgram.h"
#endif

#include "EMGFilters.h"

#include "fix_fft.h"

#define TIMING_DEBUG 1

#define sensor_input_pin1 A0
#define sensor_input_pin2 A1
#define sensor_input_pin3 A2

EMGFilters myFilter;
SAMPLE_FREQUENCY sampleRate = SAMPLE_FREQ_500HZ;
NOTCH_FREQUENCY humFreq = NOTCH_FREQ_50HZ;

static int Threshold = 0;

unsigned long timeStamp;
unsigned long timeBudget;

boolean p = false;
int d = 0;
int o[64], u[64];
char im[64], data[64];
char im_two[64], data_two[64];
int oup[64];
int val = 0;
int oup_f[8];
int oup_p[8];
int oup_d[8];
int oup_o[8];
int min=50, max=0;

boolean collect = false;
uint8_t buffer_counter = 0;
uint8_t buffer_size = 64;
char data_buffer_1[64];
char data_buffer_2[64];
char im_buffer[64];
int fourier_type = 0;

const int val_size = 8;

void setup() 
{
    myFilter.init(sampleRate, humFreq, true, true, true);
    Serial.begin(115200);
    timeBudget = 1e6 / sampleRate;
}

void loop() 
{
    timeStamp = micros();
    int sensor_1_value = analogRead(sensor_input_pin1);
    int sensor_2_value = analogRead(sensor_input_pin2);
    int sensor_3_value = analogRead(sensor_input_pin3);
    
    int data_1 = myFilter.update(sensor_1_value);
    int data_2 = myFilter.update(sensor_2_value);
    int data_3 = myFilter.update(sensor_3_value);
    
    if (TIMING_DEBUG) 
    {
      Serial.print(data_1);
      Serial.print(" ");
      Serial.print(data_2);
      Serial.print(" ");
      Serial.println(data_3);
    }
    delayMicroseconds(500);
  }