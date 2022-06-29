import pathlib
import matplotlib.pyplot as plt
import numpy as np
import statistics

import pandas as pd
from scipy import fft
from scipy.signal import find_peaks
from scipy.signal import find_peaks_cwt
import scipy.signal as signal
from scipy.signal import butter, lfilter

ELECTRODE_CSV_FILEPATH = pathlib.Path('../data/electrode_data.csv')
SAMPLE_RATE = 1000

def butter_bandpass(lowcut, highcut, fs, order=5):
    return butter(order, [lowcut, highcut], fs=fs, btype='band')

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

def plot_emg_channels(channel_1, channel_2, channel_3, title=''):
    fig = plt.figure()

    nrows = 3
    ncols = 1
    plt.subplot(nrows, ncols, 1)
    plt.title('Channel 1')
    plt.plot(channel_1)

    plt.subplot(nrows, ncols, 2)
    plt.title('Channel 2')
    plt.plot(channel_2)

    plt.subplot(nrows, ncols, 3)
    plt.title('Channel 3')
    plt.plot(channel_3)

    plt.suptitle(f'EMG Channels - {title}')
    plt.tight_layout()
    plt.show()

def plot_power_spectrum(data, title, identify_peaks=False):
    spectrum, freqs, _ = plt.magnitude_spectrum(data, Fs=SAMPLE_RATE, color='C1')

    peaks, _ = find_peaks(spectrum, prominence=1)

    peak_freqs = freqs[peaks]
    peak_loc = spectrum[peaks]

    plt.title(f'Electrode power spectrum (MS) - {title}')

    if identify_peaks:
        fig, ax = plt.subplots(figsize=(12, 10))
        plt.plot(spectrum)
        plt.plot(peaks, spectrum[peaks], "xr")
        for index in range(len(peak_loc)):
            plt.text(peak_freqs[index], peak_loc[index], f'{peak_freqs[index]:.2f}Hz', size=7.5)
    plt.show()


if __name__ == '__main__':
    electrode_data_array = np.genfromtxt(ELECTRODE_CSV_FILEPATH.absolute(), delimiter=',')

    channel_1 = electrode_data_array[:, 0]
    channel_2 = electrode_data_array[:, 1]
    channel_3 = electrode_data_array[:, 2]

    # plot_power_spectrum(channel_1, "channel 1 - Before filtering")
    # plot_power_spectrum(channel_2, "channel 2 - Before filtering")
    # plot_power_spectrum(channel_3, "channel 3 - Before filtering")
    # plot_emg_channels(channel_1, channel_2, channel_3, 'Raw')
    #
    # fs = 1000
    # lowcut = 100
    # highcut = 140
    #
    # channel_1 = butter_bandpass_filter(channel_1, lowcut, highcut, fs)
    # channel_2 = butter_bandpass_filter(channel_2, lowcut, highcut, fs)
    # channel_3 = butter_bandpass_filter(channel_3, lowcut, highcut, fs)
    # # plot_power_spectrum(channel_1, "channel 1 - After filtering")
    # # plot_power_spectrum(channel_2, "channel 2 - After filtering")
    # # plot_power_spectrum(channel_3, "channel 3 - After filtering")
    # plot_emg_channels(channel_1, channel_2, channel_3, 'After filtering')
    #
    # # create envelope
    # envelope_channel_1 = np.square(channel_1)
    # envelope_channel_1 = envelope_channel_1 if envelope_channel_1.any() > 0 else 0
    #
    # envelope_channel_2 = np.square(channel_2)
    # envelope_channel_2 = envelope_channel_2 if envelope_channel_2.any() > 0 else 0
    #
    # plt.subplot(2, 1, 1)
    # plt.title('Channel 1 Envelope')
    # plt.plot(envelope_channel_1)
    # plt.subplot(2, 1, 2)
    # plt.title('Channel 2 Envelope')
    # plt.plot(envelope_channel_2)
    # plt.show()
    #
    # pd.Series(channel_1).rolling(window=16).mean().plot(style='r')
    # plt.show()

    # TODO test code
    dt = 1 / SAMPLE_RATE
    t = np.arange(0, len(channel_1))
    signal = channel_1
    signal_clean = signal
    minsignal, maxsignal = signal.min(), signal.max()

    ## Compute Fourier Transform
    n = len(t)
    fhat = np.fft.fft(signal, n)  # computes the fft
    psd = fhat * np.conj(fhat) / n
    freq = (1 / (dt * n)) * np.arange(n)  # frequency array
    idxs_half = np.arange(1, np.floor(n / 2), dtype=np.int32)  # first half index

    ## Filter out noise
    threshold = 100
    psd_idxs = psd > threshold  # array of 0 and 1
    psd_clean = psd * psd_idxs  # zero out all the unnecessary powers
    fhat_clean = psd_idxs * fhat  # used to retrieve the signal

    signal_filtered = np.fft.ifft(fhat_clean)  # inverse fourier transform

    ## Visualization
    fig, ax = plt.subplots(4, 1)
    ax[0].plot(t, signal, color='b', lw=0.5, label='Noisy Signal')
    ax[0].plot(t, signal_clean, color='r', lw=1, label='Clean Signal')
    ax[0].set_ylim([minsignal, maxsignal])
    ax[0].set_xlabel('t axis')
    ax[0].set_ylabel('Vals')
    ax[0].legend()

    ax[1].plot(freq[idxs_half], np.abs(psd[idxs_half]), color='b', lw=0.5, label='PSD noisy')
    ax[1].set_xlabel('Frequencies in Hz')
    ax[1].set_ylabel('Amplitude')
    ax[1].legend()

    ax[2].plot(freq[idxs_half], np.abs(psd_clean[idxs_half]), color='r', lw=1, label='PSD clean')
    ax[2].set_xlabel('Frequencies in Hz')
    ax[2].set_ylabel('Amplitude')
    ax[2].legend()

    ax[3].plot(t, signal_filtered, color='r', lw=1, label='Clean Signal Retrieved')
    ax[3].set_ylim([minsignal, maxsignal])
    ax[3].set_xlabel('t axis')
    ax[3].set_ylabel('Vals')
    ax[3].legend()

    plt.subplots_adjust(hspace=0.4)
    plt.show()



