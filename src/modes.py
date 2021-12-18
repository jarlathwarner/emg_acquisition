import enum

class EMGMode(enum.Enum):
    NO_DATA = 0         # Do not send EMG data
    PREPROCESSED = 1    # Sends 50Hz rectified and band pass filtered data
    FILTERED = 2        # Sends 200Hz filtered but not rectified data
    RAW = 3             # Sends raw 200Hz data from the ADC ranged between -128 and 127
