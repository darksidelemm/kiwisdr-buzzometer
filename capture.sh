#!/bin/bash
#
# KiwiSDR PLI Measurement -> InfluxDB Collection Script
#
# Run with cron on whatever update rate you want
#

# KiwiSDR Host and port
KIWISDR_HOST="kiwisdr.areg.org.au"
KIWISDR_PORT=8075

# Test Frequency in kHz
FREQUENCY=5010
# Capture time in seconds. Leave this at 10s for now...
CAPTURE_TIME=10


# InfluxDB Settings
export INFLUXDB_URL="http://localhost:8086"
export INFLUXDB_TOKEN=""
export INFLUXDB_ORG=""
export INFLUXDB_BUCKET=""
export INFLUXDB_MEASNAME="kiwisdr_hum"

# Use a local venv if it exists
VENV_DIR=venv
if [ -d "$VENV_DIR" ]; then
    echo "Entering venv."
    source $VENV_DIR/bin/activate
fi

# Delete any old capture data
rm temp.wav

# Capture data
echo "Capturing data for $FREQUENCY kHz"
python kiwirecorder.py -s $KIWISDR_HOST -p $KIWISDR_PORT --tlimit=$CAPTURE_TIME -m am -f $FREQUENCY --fn=temp

# Process
python process_hum.py $FREQUENCY