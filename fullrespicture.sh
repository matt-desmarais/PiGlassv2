now=$(date +"%m_%d_%Y-%H:%M:%S")
echo "Filename : $now.jpg"
raspistill -rot 270 -o /home/pi/Pictures/FullRes-$now.jpg
