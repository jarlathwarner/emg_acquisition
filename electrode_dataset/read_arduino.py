import time

import numpy as np
import serial

# open serial connection
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
time.sleep(2)

sensor_data = []

start_time = time.time()
try:
    while True:
        byte_data = ser.readline()
        decoded_data = byte_data.decode()
        stripped_data = decoded_data.strip()
        split_data = stripped_data.split(' ')

        if len(split_data) > 0 and split_data != ['']:
            numeric_data = list(map(int, split_data))
            sensor_data.append(numeric_data)
except KeyboardInterrupt:
    print("Exiting recording session")

# close serial connection
ser.close()

end_time = start_time = time.time()
elapsed_time = end_time - start_time

# convert data to numpy array
max_len = len(max(sensor_data, key=len))
adjusted_data = [x + [0]*(max_len-len(x)) for x in sensor_data]
sensor_data_matrix = np.array(adjusted_data)

print(sensor_data_matrix)

# # plot the data
# plt.plot(sensor_data_matrix)
# plt.xlabel('Time')
# plt.ylabel('Sensor readings')
# plt.title('Sensor readings vs Time')
# plt.show()
