now=$(date +"%m_%d_%Y-%H:%M:%S")
echo "Filename : $now.mp4"
raspivid --timeout 0 --rotation 270        --awb auto --metering backlit --exposure auto --drc high --profile high --level 4.1 --bitrate 2250000 --framerate 25.375 --intra 90 --annotate 10 --annotate "%Y-%m-%d %X"        --output - | ffmpeg        -i -         -f alsa -channels 2 -sample_rate 22050 -itsoffset 6 -i hw:1        -c:v copy -af "volume=8.0,aresample=async=1" -c:a aac -b:a 48k        -map 0:v -map 1:a  -f flv /home/pi/Pictures/Video-$now.mp4
