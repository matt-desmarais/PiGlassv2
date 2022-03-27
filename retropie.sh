sudo systemctl stop lightdm.service
sleep 1
sudo ttyecho -n /dev/tty1 "sudo -u pi emulationstation"
#sleep 1
sudo systemctl start lightdm.service
sudo systemctl restart lightdm.service
