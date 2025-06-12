import csv
import numpy as np
from scipy import signal
import wave
import struct
from scipy.interpolate import CubicSpline

fs = 48000
numtaps = 65536

iso_freq = [20, 25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000, 20000]
iso_curves = {
		0: [76.55, 65.62, 55.12, 45.53, 37.63, 30.86, 25.02, 20.51, 16.65, 13.12, 10.09, 7.54, 5.11, 3.06, 1.48, 0.3, -0.3, -0.01, 1.03, -1.19, -4.11, -7.05, -9.03, -8.49, -4.48, 3.28, 9.83, 10.48, 8.38, 14.1, 79.65],
        10: [83.75, 75.76, 68.21, 61.14, 54.96, 49.01, 43.24, 38.13, 33.48, 28.77, 24.84, 21.33, 18.05, 15.14, 12.98, 11.18, 9.99, 10, 11.26, 10.43, 7.27, 4.45, 3.04, 3.8, 7.46, 14.35, 20.98, 23.43, 22.33, 25.17, 81.47],
        20: [89.58, 82.65, 75.98, 69.62, 64.02, 58.55, 53.19, 48.38, 43.94, 39.37, 35.51, 31.99, 28.69, 25.67, 23.43, 21.48, 20.1, 20.01, 21.46, 21.4, 18.15, 15.38, 14.26, 15.14, 18.63, 25.02, 31.52, 34.43, 33.04, 34.67, 84.18],
        40: [99.85, 93.94, 88.17, 82.63, 77.78, 73.08, 68.48, 64.37, 60.59, 56.7, 53.41, 50.4, 47.58, 44.98, 43.05, 41.34, 40.06, 40.01, 41.82, 42.51, 39.23, 36.51, 35.61, 36.65, 40.01, 45.83, 51.8, 54.28, 51.49, 51.96, 92.77],
        60: [109.51, 104.23, 99.08, 94.18, 89.96, 85.94, 82.05, 78.65, 75.56, 72.47, 69.86, 67.53, 65.39, 63.45, 62.05, 60.81, 59.89, 60.01, 62.15, 63.19, 59.96, 57.26, 56.42, 57.57, 60.89, 66.36, 71.66, 73.16, 68.63, 68.43, 104.92],
        80: [118.99, 114.23, 109.65, 105.34, 101.72, 98.36, 95.17, 92.48, 90.09, 87.82, 85.92, 84.31, 82.89, 81.68, 80.86, 80.17, 79.67, 80.01, 82.48, 83.74, 80.59, 77.88, 77.07, 78.31, 81.62, 86.81, 91.41, 91.74, 85.41, 84.67, 118.95],
        100: [128.41, 124.15, 120.11, 116.38, 113.35, 110.65, 108.16, 106.17, 104.48, 103.03, 101.85, 100.97, 100.3, 99.83, 99.62, 99.5, 99.44, 100.01, 102.81, 104.25, 101.18, 98.48, 97.67, 99, 102.3, 107.23, 111.11, 110.23, 102.07, 100.83, 133.73]
      }

def create_primary_interpolated_curves(curves):
    primary_curves = {}
    for phon in [30, 50, 70, 90]:
        lower_phon = phon - 10
        upper_phon = phon + 10
        weight = 0.5
        lower_curve = np.array(curves[lower_phon])
        upper_curve = np.array(curves[upper_phon])
        interpolated_curve = lower_curve * (1 - weight) + upper_curve * weight
        primary_curves[phon] = interpolated_curve.tolist()
    return primary_curves


def create_fine_interpolated_curves(curves, iso_freq, step=0.1):
    fine_curves = {}
    for phon in np.linspace(0.0, 100.0, int(1000/step) + 1, endpoint=True):
        rounded_phon = np.round(phon, 1)
        if rounded_phon in curves:
            fine_curves[rounded_phon] = curves[rounded_phon]
        else:
            interpolated_curve = []
            for freq in iso_freq:
                lower_phon = int(rounded_phon // 10 * 10)
                upper_phon = min(lower_phon + 10, 100)
                weight = (rounded_phon - lower_phon) / 10
                interpolated_value = np.interp(freq, iso_freq, curves[lower_phon]) * (1 - weight) + \
                                     np.interp(freq, iso_freq, curves[upper_phon]) * weight
                interpolated_curve.append(np.round(interpolated_value, 3))
            fine_curves[rounded_phon] = interpolated_curve
    return fine_curves

primary_curves = create_primary_interpolated_curves(iso_curves)

fine_curves = create_fine_interpolated_curves({**iso_curves, **primary_curves}, iso_freq)

def save_data_to_csv(data, filename):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Frequency', 'dB'])
        writer.writerows(data)

def design_fir_filter_from_phon_levels(phon1, phon2, numtaps, fs):

    db_diff = np.array(fine_curves[phon2]) - np.array(fine_curves[phon1])
    reference_db_diff = db_diff[iso_freq.index(1000)]
    relative_gains_db = db_diff - reference_db_diff
    relative_gains_linear = 10 ** (relative_gains_db / 20)
    
    print(fine_curves[phon2])
    print(fine_curves[phon1])
    print(relative_gains_db)

    full_freq_range = np.linspace(0, fs/2, numtaps)
    gain_spline = CubicSpline(iso_freq, relative_gains_linear)

    interpolated_gains = gain_spline(full_freq_range)

    interpolated_gains[-1] = 0

    fir_coeff = signal.firwin2(numtaps, full_freq_range, interpolated_gains, fs=fs)

    return fir_coeff

def save_filter_to_wav(coeff, filename, fs):
    scaled_coeff = np.int16(coeff / np.max(np.abs(coeff)) * 32767)
  
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1) 
        wav_file.setsampwidth(2) 
        wav_file.setframerate(fs)
        for sample in scaled_coeff:
            packed_sample = struct.pack('h', sample)
            wav_file.writeframes(packed_sample)

for end_phon in [80.0, 81.0, 82.0, 83.0, 84.0, 85.0, 86.0, 87.0, 88.0, 89.0, 90.0]:
    for start_phon in np.arange(60.0, end_phon + 0.1, 0.1):
        start_phon_rounded = np.round(start_phon, 1)
        end_phon_rounded = np.round(end_phon, 1)

        fir_coeff = design_fir_filter_from_phon_levels(start_phon_rounded, end_phon_rounded, numtaps, fs)
        print(fir_coeff)
        
        filename = f'{start_phon_rounded:.1f}-{end_phon_rounded}_filter.wav'

        save_filter_to_wav(fir_coeff, filename, fs)

        print(f"Created filter file: {filename}")