"""
Enum class containing the different modes that the MYO can return EMG signals
"""
import enum

class emg_mode(enum.Enum):
    NO_DATA = 0         # Do not send EMG data
    PREPROCESSED = 1    # 50Hz rectified and band pass filtered data
    FILTERED = 2        # 200Hz filtered but not rectified data
    RAW = 3             # raw 200Hz data from the ADC ranged between -128 and 127
