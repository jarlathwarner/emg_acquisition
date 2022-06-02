import time

import numpy as np
import serial

class ElectrodeSensors:
    def __init__(self):
        time.sleep(2)

        self.sensor_data = []

    def record_data(self):
        ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

        print("--- Starting recording ---")
        start_time = time.time()

        while True:
            elapsed_time = time.time() - start_time

            if elapsed_time > 3:
                print(f"Elapsed time: {elapsed_time} seconds")
                print("--- Finished recording ---")
                break

            byte_data = ser.readline()
            decoded_data = byte_data.decode('UTF-8', errors='ignore')
            stripped_data = decoded_data.strip()
            split_data = stripped_data.split(' ')

            # verify data is valid
            if len(split_data) > 0 and split_data != ['']:
                numeric_data = list(map(int, split_data))
                self.sensor_data.append(numeric_data)

        # close serial connection
        ser.close()

    def get_numpy_array(self):
        # convert data to numpy array
        max_len = len(max(self.sensor_data, key=len))
        adjusted_data = [x + [0] * (max_len - len(x)) for x in self.sensor_data]
        sensor_data_matrix = np.array(adjusted_data)
        return sensor_data_matrix
