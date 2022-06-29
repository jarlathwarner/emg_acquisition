import time

import numpy as np
import serial

from constants import GESTURE_DURATION_SECONDS
from constants import SAMPLE_RATE

class ElectrodeSensors:
    def __init__(self):
        self.sensor_data = []
        self.sensor_labels = []
        self.sample_duration = 1 / SAMPLE_RATE

    def record_data(self, label):
        ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

        print("+--- Starting recording ---")
        start_time = time.time()

        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time > GESTURE_DURATION_SECONDS:
                print(f"| Elapsed time: {elapsed_time} seconds")
                print("+--- Finished recording ---\n")
                break

            start_recording_time = time.time()
            byte_data = ser.readline()
            decoded_data = byte_data.decode('UTF-8', errors='ignore')
            stripped_data = decoded_data.strip()
            split_data = stripped_data.split(' ')

            # verify data is valid
            if len(split_data) > 0 and split_data != [''] and '-' not in split_data:
                numeric_data = list(map(int, split_data))
                self.sensor_data.append(numeric_data)
                self.sensor_labels.append(label)

            # control sample rate
            elapsed_recording_time = time.time() - start_recording_time
            if elapsed_recording_time < self.sample_duration:
                time.sleep(self.sample_duration - elapsed_recording_time)

        # close serial connection
        ser.close()

    def get_sensor_data_array(self):
        # convert data to numpy array
        max_len = len(max(self.sensor_data, key=len))
        adjusted_data = [x + [0] * (max_len - len(x)) for x in self.sensor_data]
        sensor_data_matrix = np.array(adjusted_data)
        return sensor_data_matrix

    def get_dataset_array(self):
        # convert data to numpy array
        sensor_data_array = self.get_sensor_data_array()
        label_array = np.array(self.sensor_labels)

        # append labels to sensor data
        dataset_matrix = np.column_stack((sensor_data_array, label_array))
        return dataset_matrix

    def reset_data(self):
        # convert data to numpy array
        self.sensor_data = []
        self.sensor_labels = []
