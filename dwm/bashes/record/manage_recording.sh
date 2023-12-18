#!/bin/bash

pid_file="pid.txt"
recording_file="myrecording.wav"
server_address="localhost"
server_port="5001"

# Function to start recording
start_recording() {
    arecord -f cd -t wav $recording_file &
    echo $! > $pid_file
    echo "Recording started with PID $!"
}

# Function to stop recording and send a request to the server
# Function to stop recording and request transcription
stop_recording_and_request_transcription() {
    if [ -f $pid_file ]; then
        kill $(cat $pid_file)
        rm $pid_file
        echo "Recording stopped."

        # Requesting transcription from the server
        echo "Requesting transcription from the server..."
        response=$(echo | nc $server_address $server_port)

        # Display the response as a banner and copy it to clipboard
		echo "$response" | figlet | xargs -I{} notify-send "{}"
        echo "$response" | xclip -selection clipboard

        # Keep the banner displayed for a certain duration
        sleep $display_duration
    else
        echo "No recording is currently running."
    fi
}

# Main logic
if [ -f $pid_file ]; then
    # If recording is in progress, stop it and send a request
    stop_recording_and_request_transcription
else
    # If no recording is in progress, start a new one
    start_recording
fi
