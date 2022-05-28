// /*
// * Copyright 2017, OYMotion Inc.
// * All rights reserved.
// *
// * Redistribution and use in source and binary forms, with or without
// * modification, are permitted provided that the following conditions
// * are met:
// *
// * 1. Redistributions of source code must retain the above copyright
// *    notice, this list of conditions and the following disclaimer.
// *
// * 2. Redistributions in binary form must reproduce the above copyright
// *    notice, this list of conditions and the following disclaimer in
// *    the documentation and/or other materials provided with the
// *    distribution.
// *
// * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
// * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
// * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
// * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
// * COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
// * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
// * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
// * OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
// * AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
// * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
// * THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
// * DAMAGE.
// *
// */

// #if defined(ARDUINO) && ARDUINO >= 100
// #include "Arduino.h"
// #else
// #include "WProgram.h"
// #endif

// #include "EMGFilters.h"

// #define TIMING_DEBUG 1

// // Sensor input pins
// #define sensor1InputPin A0 
// #define sensor2InputPin A1
// #define sensor3InputPin A2

// EMGFilters myFilter;
// SAMPLE_FREQUENCY sampleRate = SAMPLE_FREQ_1000HZ;
// NOTCH_FREQUENCY humFreq = NOTCH_FREQ_50HZ;

// // Calibration:
// // put on the sensors, and release your muscles;
// // wait a few seconds, and select the max value as the threshold;
// // any value under threshold will be set to zero
// static int Threshold = 0;

// unsigned long timeStamp;
// unsigned long timeBudget;

// void setup() 
// {
//     /* add setup code here */
//     myFilter.init(sampleRate, humFreq, true, true, true);

//     // open serial
//     Serial.begin(115200);

//     // setup for time cost measure
//     // using micros()
//     timeBudget = 1e6 / sampleRate;
//     // micros will overflow and auto return to zero every 70 minutes
// }

// void loop() 
// {
//     /* add main program code here */
//     // In order to make sure the ADC sample frequence on arduino,
//     // the time cost should be measured each loop
//     /*------------start here-------------------*/
//     timeStamp = micros();

//     int sensor1Value = analogRead(sensor1InputPin);
//     int sensor2Value = analogRead(sensor2InputPin);
//     int sensor3Value = analogRead(sensor3InputPin);

//     // convert reading to voltage
//     int sensor1Voltage = (float)sensor1Value *5 / 1023;
//     int sensor2Voltage = (float)sensor2Value *5 / 1023;
//     int sensor3Voltage = (float)sensor3Value *5 / 1023;

//     // filter processing
//     // int filteredDataSensor1 = myFilter.update(sensor1Value);
//     // int filteredDataSensor2 = myFilter.update(sensor2Value);
//     // int filteredDataSensor3 = myFilter.update(sensor3Value);

//     // int envlope = sq(DataAfterFilter);
//     // any value under threshold will be set to zero
//     // envlope = (envlope > Threshold) ? envlope : 0;
    
//     timeStamp = micros() - timeStamp;
//     if (TIMING_DEBUG) 
//     {
        
//         // Serial.print("Sensor data 1: "); Serial.println(filteredDataSensor1);
//         // Serial.print("Sensor data 2: "); Serial.println(filteredDataSensor2);
//         // Serial.print("Sensor data 3: "); Serial.println(filteredDataSensor3);

//         // Serial.print(filteredDataSensor1);
//         // Serial.print(", ");
//         // Serial.print(filteredDataSensor2);
//         // Serial.print(", ");
//         // Serial.print(filteredDataSensor3);
//         // Serial.println();
                

//         // Serial.print(sensor1Value);
//         // Serial.print(", ");
//         // Serial.print(sensor2Value);
//         // Serial.print(", ");
//         // Serial.print(sensor3Value);
//         // Serial.println();

//         Serial.print(sensor1Voltage);
//         Serial.print(", ");
//         Serial.print(sensor2Voltage);
//         Serial.print(", ");
//         Serial.print(sensor3Voltage);
//         Serial.println();

        
//         // float sensor1ValueF = (float)sensor1Value *5 / 1023;
//         // float sensor2ValueF = (float)sensor2Value *5 / 1023;
//         // float sensor3ValueF = (float)sensor3Value *5 / 1023;
//         // Serial.print(sensor1ValueF);
//         // Serial.print(", ");
//         // Serial.print(sensor2ValueF);
//         // Serial.print(", ");
//         // Serial.print(sensor3ValueF);
//         // Serial.println();
//     }

//     /*------------end here---------------------*/
//     // if less than timeBudget, then you still have (timeBudget - timeStamp) to
//     // do your work
//     delayMicroseconds(500);
//     // if more than timeBudget, the sample rate need to reduce to
//     // SAMPLE_FREQ_500HZ
// }


#if defined(ARDUINO) && ARDUINO >= 100
#include "Arduino.h"
#else
#include "WProgram.h"
#endif

#include "EMGFilters.h"

#include "fix_fft.h"

#define TIMING_DEBUG 1

#define SensorInputPin A0 // input pin number

#define SensorInputPin_two A1

EMGFilters myFilter;
SAMPLE_FREQUENCY sampleRate = SAMPLE_FREQ_1000HZ;
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

const int val_size = 8;

void setup() {
    myFilter.init(sampleRate, humFreq, true, true, true);
    Serial.begin(115200);
    timeBudget = 1e6 / sampleRate;
}

void loop() {
    timeStamp = micros();
    int Value = analogRead(SensorInputPin);
    int Value_two = analogRead(SensorInputPin_two);
    
    int DataAfterFilter = myFilter.update(Value);
    int DataAfterFilter_two = myFilter.update(Value_two);
  
    int envlope = sq(DataAfterFilter);
    int envlope_two = sq(DataAfterFilter_two);
    
    envlope = (envlope > Threshold) ? envlope : 0;
    envlope_two = (envlope_two > Threshold) ? envlope_two : 0;
    timeStamp = micros() - timeStamp;
    
    if (TIMING_DEBUG) {
        if (envlope > 500 && envlope_two > 500 && p == false){
          p = true;
          d = 0;
          o[64] = {};
          u[64] = {};
        }
        if (p == true){
          o[d] = envlope;
          u[d] = envlope_two;
          d+=1;
        }
        if(d == 63){
          d = 0;
          p == false;

          min=50, max=0;
          for (int i = 0; i < 64; i++) { 
            data[i] = o[i] / 4 - 64; 
            im[i] = 0;
            if(val>max) max=val;
            if(val<min) min=val; 
          }
          fix_fft(data, im, 5, 0);
          
          min=50, max=0;
          for (int i = 0; i < 64; i++) { 
            data_two[i] = u[i] / 4 - 64; 
            im_two[i] = 0;
            if(val>max) max=val;
            if(val<min) min=val; 
          }
          fix_fft(data_two, im_two, 5, 0);

          int f = 0;
          for (int i = 0;i < 64;i++){
            oup[i] = int(data[i]-data_two[i]);
            if (i%4 == 0){
              oup_f[f] = (oup[i]-oup[i-2])-(oup[i-1]-oup[i-3]);
              f++;
            }
          }
          f = 0;
          for (int i = 0;i < 16;i++){

            if (i%2 == 0){
              oup_d[f] = ((oup_f[i])-(oup_f[i-1]));
              //Serial.print(abs((oup_d[f]+(oup_p[f]))));
              //Serial.print(" , ");
              oup_o[f]=abs((oup_d[f]+(oup_p[f])));
              f++;
            }
            for (int i=0; i<val_size; i++){
            int high = (oup_o[i] >> 9) & 127;
            int low  = oup_o[i] & 127;
            Serial.print(128+i);
            Serial.print(", ");
            Serial.print(high);
            Serial.print(", ");
            Serial.print(low);
            Serial.println();
          }
          }
          //Serial.println("");
          for (int i=0;i<8;i++){oup_p[i] = oup_d[i];}
        }
      }
      delayMicroseconds(500);
    }