import os
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt, spectrogram
import matplotlib.pyplot as plt

def odd_number(x):
    return np.where(np.mod(np.ceil(x), 2) == 0, np.ceil(x) + 1, np.ceil(x))

class ImageGenerator:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
        self.ts = 0.0082  # Sample time in sec
        self.Bw = 2.5e+09
        self.sections = 8  # Number of sections
        
        self.I_raw_data, self.Q_raw_data = self.load_data()
        self.rm = self.combine_data()
        
        self.II, self.JJ = self.rm.shape
        self.win = np.ones((self.rm.shape[0], self.rm.shape[1]))
        self.NTS = self.II
        self.fs = self.NTS / self.ts
        self.Tsweep = self.ts
        
        self.Data_range = self.perform_fft()
        self.Data_range_MTI = self.apply_high_pass_filter()
        self.MD = self.define_md_parameters()
        self.Data_spec_MTI2 = self.compute_spectrogram()

    def load_data(self):
        part_I_raw_name = 'I_raw'
        part_Q_raw_name = 'Q_raw'
        file_list = [f for f in os.listdir(self.input_path) if f.endswith('.csv')]
        
        I_raw_name = next((file for file in file_list if part_I_raw_name in file), None)
        Q_raw_name = next((file for file in file_list if part_Q_raw_name in file), None)

        I_raw_data = pd.read_csv(os.path.join(self.input_path, I_raw_name), header=None, skiprows=1).iloc[:, 3:].values
        Q_raw_data = pd.read_csv(os.path.join(self.input_path, Q_raw_name), header=None, skiprows=1).iloc[:, 3:].values

        print(f'Loaded data successfully from {self.input_path}') 
        return I_raw_data, Q_raw_data

    def combine_data(self):
        rm = (self.I_raw_data + 1j * self.Q_raw_data).T
        print ('rm shape:', rm.shape)
        return rm

    def perform_fft(self):
        tmp = np.fft.fftshift(np.fft.fft(self.rm * self.win, axis=0), axes=0)
        data_range = tmp[self.NTS // 2:self.NTS, :]
        print ('Data_range shape:', data_range.shape)
        return data_range

    def apply_high_pass_filter(self):
        ns = (self.Data_range.shape[1])
        Data_range_MTI = np.zeros((self.Data_range.shape[0], ns), dtype=complex)
        b, a = butter(4, 0.0075, 'high')
        for k in range(self.Data_range.shape[0]):
            Data_range_MTI[k, :] = filtfilt(b, a, self.Data_range[k, :])
        return Data_range_MTI[1:, :]

    def define_md_parameters(self):
        MD = {
            'PRF': 1 / self.Tsweep,
            'TimeWindowLength': 16,
            'OverlapFactor': 0,
            'OverlapLength': 0,
            'Pad_Factor': 8,
            'FFTPoints': 8 * 16,
            'DopplerBin': 1 / self.Tsweep / (8 * 16),
            'DopplerAxis': np.arange(-1 / self.Tsweep / (8 * 16) / 2, 1 / self.Tsweep / (8 * 16) / 2, 1 / self.Tsweep / (8 * 16)),
            'WholeDuration': self.Data_range_MTI.shape[1] / (1 / self.Tsweep),
            'NumSegments': (self.Data_range_MTI.shape[1] - 16) // (16 * (1 - 0))
        }
        return MD

    def compute_spectrogram(self):
        Data_spec_MTI2 = np.zeros((self.MD['FFTPoints'], int(self.Data_range_MTI.shape[1] / self.MD['TimeWindowLength'])), dtype=complex)
        bin_indl = 0
        bin_indu = min(93, self.Data_range_MTI.shape[0])  # Adjust for zero-based index

        for RBin in range(bin_indl, bin_indu):
            _, _, Data_MTI_temp = spectrogram(self.Data_range_MTI[RBin, :], nperseg=self.MD['TimeWindowLength'], noverlap=self.MD['OverlapLength'], nfft=self.MD['FFTPoints'], axis=0, return_onesided=False)
            Data_spec_MTI2 += np.fft.fftshift(Data_MTI_temp, axes=0)

        self.MD['TimeAxis'] = np.linspace(0, self.MD['WholeDuration'], Data_spec_MTI2.shape[1])
        return np.flipud(Data_spec_MTI2)

    def plot_and_save_images(self):
        sec_length = self.Data_spec_MTI2.shape[1] // self.sections

        for sec in range(1, self.sections + 1):
            plt.figure(1, figsize=(8.84, 6.63))  # Set the figure size to 884x663 pixels
            
            doppler_min = self.MD['DopplerAxis'].min() * 3e8 / 2 / 5.8e9
            doppler_max = self.MD['DopplerAxis'].max() * 3e8 / 2 / 5.8e9
            
            if doppler_min == doppler_max:
                doppler_max += 1e-5  # Add a small offset
            
            plt.imshow(20 * np.log10(np.abs(self.Data_spec_MTI2[:, (sec - 1) * sec_length:sec * sec_length])), 
                       aspect='auto', 
                       extent=[self.MD['TimeAxis'][0], self.MD['TimeAxis'][-1], doppler_min, doppler_max])
            
            plt.gca().set_position([0, 0, 1, 1])  # Tight layout
            plt.gca().set_yticks([])
            plt.gca().set_xticks([])
            
            pic_path = os.path.join(self.output_path, f'radar1_0{sec}')
            os.makedirs(pic_path, exist_ok=True)
            
            plt.savefig(os.path.join(pic_path, f'{sec}.jpg'))
            plt.close()

    def generate(self):
        self.plot_and_save_images()

# Usage
if __name__ == '__main__':
    input_path = 'sample_raw_radar_dataset_without_image/1'
    destination_dir = 'spectrogram/1'
    generator = ImageGenerator(input_path, destination_dir)
    generator.generate()
