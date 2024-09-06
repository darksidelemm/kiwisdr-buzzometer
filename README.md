# KiwiSDR Buzz-O-Meter
Some scripts to collect statistics on powerline interference levels using a KiwiSDR, and push them into InfluxDB for plotting.

This works by collecting AM-demodulated audio, and measuring the SNR of the 100 Hz tone present. Averaging is performed over about 5 seconds of recording

Very rough-and-ready. 

Notes:
* Not intended to provide absolute metrics. Only the SNR output is going to be useful.
* No clear-channel checking. Metrics can and will be affected by other signals present on the test frequency.

## Dependencies
```console
python3 -m venv venv
pip install -r requirements.txt
```

## Configuration
* Update settings in capture.sh
* Run capture.sh in a cronjob