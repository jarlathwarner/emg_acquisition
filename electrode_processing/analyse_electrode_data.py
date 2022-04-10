import pathlib
import matplotlib.pyplot as plt
import numpy as np
import statistics

from scipy.signal import find_peaks
from scipy.signal import find_peaks_cwt
import scipy.signal as signal

ELECTRODE_CSV_FILEPATH = pathlib.Path('../data/electrode_data.csv')

def plot_power_spectrum(data, title):
    sample_rate = 1000

    spectrum, freqs, _ = plt.magnitude_spectrum(data, Fs=sample_rate, color='C1')

    peaks, _ = find_peaks(spectrum, prominence=1)

    peak_freqs = freqs[peaks]
    peak_loc = spectrum[peaks]

    plt.title(f'Electrode power spectrum (MS) - {title}')
    plt.show()

    fig, ax = plt.subplots(figsize=(12, 8))
    plt.plot(spectrum)
    plt.plot(peaks, spectrum[peaks], "xr")
    for index in range(len(peak_loc)):
        plt.text(peak_freqs[index], peak_loc[index], f'{peak_freqs[index]:.2f}Hz', size=7.5)
    plt.show()


if __name__ == '__main__':
    electrode_data_array = np.genfromtxt(ELECTRODE_CSV_FILEPATH.absolute(), delimiter=',')

    plot_power_spectrum(electrode_data_array[:, 0], "channel 1")
    # plot_power_spectrum(electrode_data_array[:, 1], "channel 2")
    # plot_power_spectrum(electrode_data_array[:, 2], "channel 3")


