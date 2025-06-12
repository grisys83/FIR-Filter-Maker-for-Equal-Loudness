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
		0: [76.5517, 65.6189, 55.1228, 45.5340, 37.6321, 30.8650, 25.0238, 20.5100, 16.6458, 13.1160, 10.0883, 7.5436, 5.1137, 3.0589, 1.4824, 0.3029, -0.3026, -0.0103, 1.0335, -1.1863, -4.1116, -7.0462, -9.0260, -8.4944, -4.4829, 3.2817, 9.8291, 10.4757, 8.3813, 14.1000, 79.6500],
        10: [83.7500, 75.7579, 68.2089, 61.1365, 54.9638, 49.0098, 43.2377, 38.1338, 33.4772, 28.7734, 24.8417, 21.3272, 18.0522, 15.1379, 12.9768, 11.1791, 9.9918, 9.9996, 11.2621, 10.4291, 7.2744, 4.4508, 3.0404, 3.7961, 7.4583, 14.3483, 20.9841, 23.4306, 22.3269, 25.1700, 81.4700],
        20: [89.5781, 82.6513, 75.9764, 69.6171, 64.0178, 58.5520, 53.1898, 48.3809, 43.9414, 39.3702, 35.5126, 31.9922, 28.6866, 25.6703, 23.4263, 21.4825, 20.1011, 20.0052, 21.4618, 21.4013, 18.1515, 15.3844, 14.2559, 15.1415, 18.6349, 25.0196, 31.5227, 34.4256, 33.0444, 34.6700, 84.1800],
        40: [99.8539, 93.9444, 88.1659, 82.6287, 77.7849, 73.0825, 68.4779, 64.3711, 60.5855, 56.7022, 53.4087, 50.3992, 47.5775, 44.9766, 43.0507, 41.3392, 40.0618, 40.0100, 41.8195, 42.5076, 39.2296, 36.5090, 35.6089, 36.6492, 40.0077, 45.8283, 51.7968, 54.2841, 51.4859, 51.9600, 92.7700],
        60: [109.5113,  104.2279, 99.0779, 94.1773, 89.9635, 85.9434, 82.0534, 78.6546, 75.5635, 72.4743, 69.8643, 67.5348, 65.3917, 63.4510, 62.0512, 60.8150, 59.8867, 60.0116, 62.1549, 63.1894, 59.9616, 57.2552, 56.4239, 57.5699, 60.8882, 66.3613, 71.6640, 73.1551, 68.6308, 68.4300, 104.9200],
        80: [118.9900, 114.2326, 109.6457, 105.3367, 101.7214, 98.3618, 95.1729, 92.4797, 90.0892, 87.8162, 85.9166, 84.3080, 82.8934, 81.6786, 80.8634, 80.1736, 79.6691, 80.0121, 82.4834, 83.7408, 80.5867, 77.8847, 77.0748, 78.3124, 81.6182, 86.8087, 91.4062, 91.7361, 85.4068, 84.6700, 118.9500],
        100: [128.4100, 124.1500, 120.1100, 116.3800, 113.3500, 110.6500, 108.1600, 106.1700, 104.4800, 103.0300, 101.8500, 100.9700, 100.300, 99.8300, 99.6200, 99.500, 99.4400, 100.0100, 102.8100, 104.2500, 101.1800, 98.4800, 97.6700, 9900, 102.300, 107.2300, 111.1100, 110.2300, 102.0700, 100.8300, 133.7300]
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