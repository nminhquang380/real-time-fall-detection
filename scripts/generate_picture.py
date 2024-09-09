import os
import numpy as np
import pandas as pd
from scipy.signal import butter, freqz, spectrogram
import matplotlib.pyplot as plt

def oddnumber(x):
    # Get a nearest odd number of x
    nx = len(x)
    y = np.zeros(nx)
    for k in range(nx):
        y[k] = np.floor(x[k])
        if y[k] % 2 == 0:
            y[k] = np.ceil(x[k])
        if y[k] % 2 == 0:
            y[k] += 1
    return y

def generate_pic(file_path):
    part_I_raw_name = 'I_raw'
    part_Q_raw_name = 'Q_raw'
    file_list = [f for f in os.listdir(file_path) if f.endswith('.csv')]
    
    I_raw_name = None
    Q_raw_name = None
    for file in file_list:
        if part_I_raw_name in file:
            I_raw_name = file
        if part_Q_raw_name in file:
            Q_raw_name = file

    ts = 0.0082  # Sample time in sec

    # Read the I_raw data starting from the 2nd row and 4th column
    I_raw_data = pd.read_csv(os.path.join(file_path, I_raw_name), header=None, skiprows=1).iloc[:, 3:].values

    # Read the Q_raw data starting from the 2nd row and 4th column
    Q_raw_data = pd.read_csv(os.path.join(file_path, Q_raw_name), header=None, skiprows=1).iloc[:, 3:].values

    # Combine the real and imaginary parts into a complex matrix
    rm = (I_raw_data + 1j * Q_raw_data).T

    II, JJ = rm.shape  # Range map vector [rangebins x slowtime samples]
    print(f'The slowtime bins are: \t{JJ} \nthe range bins are: \t{II}\n')

    win = np.ones((rm.shape[0], rm.shape[1]))
    NTS = II
    fs = NTS / ts
    Tsweep = ts
    Bw = 2.5e+09

    Data_time = rm[:, :]

    # Perform FFT on the data
    tmp = np.fft.fftshift(np.fft.fft(Data_time * win, axis=0), axes=0)
    Data_range = tmp[NTS // 2:NTS, :]
    
    # Calculate the number of columns (ns) in the range data
    ns = Data_range.shape[1]
    Data_range_MTI = np.zeros((Data_range.shape[0], ns), dtype=complex)

    # High-pass filter using a Butterworth filter
    b, a = butter(4, 0.0075, 'high')
    for k in range(Data_range.shape[0]):
        Data_range_MTI[k, :] = np.convolve(Data_range[k, :], b, mode='same')

    # Frequency and range axis
    freq = np.arange(ns) * fs / (2 * ns)
    range_axis = (freq * 3e8 * Tsweep) / (2 * Bw)
    Data_range_MTI = Data_range_MTI[1:, :]
    Data_range = Data_range[1:, :]

    bin_indl = 1
    bin_indu = min(92, Data_range_MTI.shape[0] - 1)  # Adjust for zero-based index

    # Define MD parameters
    MD = {
        'PRF': 1 / Tsweep,
        'TimeWindowLength': 16,
        'OverlapFactor': 0,
        'OverlapLength': 0,
        'Pad_Factor': 8,
        'FFTPoints': 8 * 16,
        'DopplerBin': 1 / Tsweep / (8 * 16),
        'DopplerAxis': np.arange(-1 / Tsweep / (8 * 16) / 2, 1 / Tsweep / (8 * 16) / 2, 1 / Tsweep / (8 * 16)),
        'WholeDuration': Data_range_MTI.shape[1] / (1 / Tsweep),
        'NumSegments': (Data_range_MTI.shape[1] - 16) // (16 * (1 - 0))
    }

    # Adjust initialization of Data_spec_MTI2 based on the first spectrogram output
    _, _, Data_MTI_temp = spectrogram(Data_range_MTI[bin_indl, :], nperseg=MD['TimeWindowLength'], noverlap=MD['OverlapLength'], nfft=MD['FFTPoints'], axis=0, return_onesided=False)
    Data_spec_MTI2 = np.zeros_like(Data_MTI_temp, dtype=complex)
    Data_spec2 = np.zeros_like(Data_MTI_temp, dtype=complex)
    
    for RBin in range(bin_indl, bin_indu + 1):
        _, _, Data_MTI_temp = spectrogram(Data_range_MTI[RBin, :], nperseg=MD['TimeWindowLength'], noverlap=MD['OverlapLength'], nfft=MD['FFTPoints'], axis=0, return_onesided=False)
        Data_spec_MTI2 += np.fft.fftshift(Data_MTI_temp, axes=0)
        
        _, _, Data_temp = spectrogram(Data_range[RBin, :], nperseg=MD['TimeWindowLength'], noverlap=MD['OverlapLength'], nfft=MD['FFTPoints'], axis=0, return_onesided=False)
        Data_spec2 += np.fft.fftshift(Data_temp, axes=0)

    MD['TimeAxis'] = np.linspace(0, MD['WholeDuration'], Data_spec_MTI2.shape[1])

    Data_spec_MTI2 = np.flipud(Data_spec_MTI2)

    sections = 8  # Number of sections
    sec_length = Data_spec_MTI2.shape[1] // sections
    
    # print(Data_spec_MTI2)
    # print(MD)

    # for sec in range(1, sections + 1):
    #     plt.imshow(20 * np.log10(np.abs(Data_spec_MTI2[:, (sec - 1) * sec_length:sec * sec_length])), aspect='auto', extent=[MD['TimeAxis'][0], MD['TimeAxis'][-1], MD['DopplerAxis'].min() * 3e8 / 2 / 5.8e9, MD['DopplerAxis'].max() * 3e8 / 2 / 5.8e9])
    #     # plt.axis('normal')
    #     plt.xticks([])
    #     plt.yticks([])
    #     pic_path = os.path.join(file_path, f'radar1_0{sec}')
    #     os.makedirs(pic_path, exist_ok=True)
    #     plt.savefig(os.path.join(pic_path, f'{sec}.jpg'))
    #     plt.close()
        
    for sec in range(1, sections + 1):
        plt.figure(1)
        
        # Calculate Doppler axis values, adding a small offset if needed
        doppler_min = MD['DopplerAxis'].min() * 3e8 / 2 / 5.8e9
        doppler_max = MD['DopplerAxis'].max() * 3e8 / 2 / 5.8e9
        
        # Ensure the y-axis limits are not identical
        if doppler_min == doppler_max:
            doppler_max += 1e-5  # Add a small offset
        
        # Debugging: Print Doppler min and max to check the values
        print(f"Doppler min: {doppler_min}, Doppler max: {doppler_max}")
        
        # Plot the image
        plt.imshow(20 * np.log10(np.abs(Data_spec_MTI2[:, (sec - 1) * sec_length:sec * sec_length])), 
                aspect='auto', 
                extent=[MD['TimeAxis'][0], MD['TimeAxis'][-1], doppler_min, doppler_max])
        
        plt.gca().set_position([0, 0, 1, 1])  # Set the position to be tight
        plt.gca().set_yticks([])
        plt.gca().set_xticks([])
        
        pic_path = os.path.join(file_path, f'radar1_0{sec}')
        os.makedirs(pic_path, exist_ok=True)
        
        # Save the image
        plt.savefig(os.path.join(pic_path, f'{sec}.jpg'))
        plt.close()