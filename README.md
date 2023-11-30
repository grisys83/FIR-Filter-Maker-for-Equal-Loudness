# FIR-Filter-Maker-for-Equal-Loudness
Generating FIR filters to balance tones at low volumes.

## Overview
This script, FIR_LOUDNESS.py, is designed to generate Finite Impulse Response (FIR) filters based on ISO 226:2003 equal-loudness contours. The primary purpose is to create EQ adjustments that maintain a consistent tonal balance at lower volume levels, typically in the range of 80 to 90 dB. 2766 WAV-files can be used in Equalizer APO <https://equalizerapo.com> and APO-loudness <https://github.com/grisys83/APO-Loudness>, or other convolution hosts such as Easy Convolver <https://www.genuinesoundware.com/?a=showproduct&b=49>.

## Dependencies
To run this script, you need the following Python libraries:

numpy
scipy
wave

These can be installed via pip using the command: pip install numpy scipy wave.

## Implementation Details
Executing python fir_filter.py initiates the script to generate a total of 2766 WAV files, starting from 60.0-80.0_filter.wav to 90.0_90.0_filter.wav. The numbers before and after the '-' in the file names represent the two phon curves used to calculate the gain for creating the FIR filters. The script automatically generates 400 curves between 60.0 and 100.0 phon based on the ISO 226:2003 standard. It then normalizes these curves at 1 kHz and calculates the difference to determine the gain values for the EQ FIR filter. Cubic spline interpolation is also employed for smoother transitions between frequencies.

## License and Acknowledgments
This script is released under the GNU General Public License version 3 (GPLv3).

## Contact Information
For questions or feedback regarding this script, please contact 136304138+grisys83@users.noreply.github.com
