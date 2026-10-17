import csv
import pathlib
import numpy as np

NUM_CHANNELS = 3
ELECTRODE_DATA_FILEPATH = pathlib.Path('../data/electrode_data.txt')
ELECTRODE_CSV_FILEPATH = pathlib.Path(ELECTRODE_DATA_FILEPATH.parent, 'electrode_data.csv')

electrode_data_file = open(ELECTRODE_DATA_FILEPATH.absolute())
csv_reader = csv.reader(electrode_data_file)

csv_rows = []
for row in csv_reader:
    converted_row = list(map(int, row))
    csv_rows.append(converted_row)

electrode_data_array = np.array(csv_rows)
np.savetxt(ELECTRODE_CSV_FILEPATH.absolute(), electrode_data_array, delimiter=',', fmt='%.3f')
