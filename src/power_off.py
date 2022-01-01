"""
Script to power off the MYO device
"""
from modes import emg_mode
from myo_interface import Myo

m = Myo(mode=emg_mode.PREPROCESSED)
m.power_off()
