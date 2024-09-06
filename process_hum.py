#!/usr/bin/env python
#
# Tapo P110 to InfluxDB Collection
#
import influxdb_client, os, time, sys, wave
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from pprint import pprint
import numpy as np

# Collect Environment Variables
INFLUXDB_URL = os.environ.get("INFLUXDB_URL")
INFLUXDB_TOKEN = os.environ.get("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.environ.get("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.environ.get("INFLUXDB_BUCKET")
INFLUXDB_MEASNAME = os.environ.get("INFLUXDB_MEASNAME")

frequency = sys.argv[1]

print(f"InfluxDB URL: \t{INFLUXDB_URL}")
print(f"InfluxDB Token: \t{INFLUXDB_TOKEN}")
print(f"InfluxDB Org: \t{INFLUXDB_ORG}")
print(f"InfluxDB Bucket: \t{INFLUXDB_BUCKET}")
print(f"InfluxDB Measurement Name: \t{INFLUXDB_MEASNAME}")
print(f"Measurement Frequency: \t{frequency} kHz")




# Read in wave file
fp = wave.open('temp.wav')
nchan = fp.getnchannels()
N = fp.getnframes()
samp_rate = fp.getframerate()
dstr = fp.readframes(N*nchan)
data = np.frombuffer(dstr, np.int16)/32768.0

NFFT_SECONDS = 8
NFFT = samp_rate

if len(data) < (samp_rate*(NFFT_SECONDS+1)):
    print("Not enough samples!")
    sys.exit(1)

# Remove the first second of data, to avoid any AGC initialization issues
data_clipped = data[samp_rate:samp_rate+NFFT_SECONDS*samp_rate]

fft_scale = (np.fft.fftfreq(samp_rate) * samp_rate)[:NFFT//2]

print("Performing FFT")
window = np.hanning(samp_rate)

output = np.array([])
for i in range(NFFT_SECONDS):
    _data = data_clipped[i*samp_rate:(i+1)*samp_rate]
    _data_fft = np.abs(np.fft.fft(_data*window))
    output = np.append(output,_data_fft)

data_fft = np.mean(output.reshape(NFFT_SECONDS,samp_rate),axis=0)[:NFFT//2]


# Extract the median value, for use as our noise floor comparison
noise_floor = np.median(20*np.log10(data_fft[:int(len(data_fft)*0.5)]))
print(f"Median Value (noise floor): {noise_floor} dB")

HUM_FREQ = 100
HUM_RANGE = 1

hum_power = 20*np.log10(np.sum(data_fft[(fft_scale>(HUM_FREQ-HUM_RANGE)) & (fft_scale < (HUM_FREQ+HUM_RANGE))]))

print(f"100Hz Hum Power: {hum_power} dB")

hum_snr = hum_power - noise_floor

print(f"100Hz Hum SNR: {hum_snr} dB")


import matplotlib.pyplot as plt
plt.plot(fft_scale,20*np.log10(data_fft))
plt.show()

meas_point = {
    "measurement": INFLUXDB_MEASNAME,
    "tags": {"name": f"{frequency} kHz"},
    "fields": {'noise_floor': float(noise_floor), 'hum_power': float(hum_power), 'hum_snr': float(hum_snr)}
}

print(meas_point)

# # Push into InfluxDB
write_client = influxdb_client.InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = write_client.write_api(write_options=SYNCHRONOUS)
write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=meas_point)

print("Done!")