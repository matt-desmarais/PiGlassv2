raspivid --timeout 0 --width 1280 --height 720 --rotation 270 --profile high --level 4.1 --bitrate 2250000 --framerate 25.375 --intra 90 --annotate 4 --annotate 8 --output - | ffmpeg -i - -f alsa -channels 2 -sample_rate 22050 -itsoffset 6 -i hw:1 -c:v copy -af "volume=8.0,aresample=async=1" -c:a aac -b:a 48k -map 0:v -map 1:a  -f flv rtmp://a.rtmp.youtube.com/live2/

