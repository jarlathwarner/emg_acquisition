import time

import numpy as np
import serial
# open serial connection
from matplotlib import pyplot as plt

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
time.sleep(2)

sensor_data = []

print("--- Starting recording -- ")
start_time = time.time()
try:
    while True:
        elapsed_time = time.time() - start_time

        if int(elapsed_time) == 2:
            print("Passed 2 seconds")
        elif int(elapsed_time) == 5:
            print("Passed 5 seconds")

        byte_data = ser.readline()
        decoded_data = byte_data.decode('UTF-8', errors='replace')
        stripped_data = decoded_data.strip()
        split_data = stripped_data.split(' ')

        # verify data is valid
        if len(split_data) > 0 and split_data != ['']:
            numeric_data = list(map(int, split_data))
            sensor_data.append(numeric_data)
except KeyboardInterrupt:
    print("Exiting recording session")

# close serial connection
ser.close()

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time:.2f} seconds")

# convert data to numpy array
max_len = len(max(sensor_data, key=len))
adjusted_data = [x + [0]*(max_len-len(x)) for x in sensor_data]
sensor_data_matrix = np.array(adjusted_data)

print(sensor_data_matrix)
print(f"Shape of sensor data matrix: {sensor_data_matrix.shape}")

# plot the data
plt.plot(sensor_data_matrix)
plt.xlabel('Time')
plt.ylabel('Sensor readings')
plt.title('Sensor readings vs Time')
plt.show()
