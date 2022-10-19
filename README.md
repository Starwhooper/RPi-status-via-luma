# RPi-status-via-luma #

To provide the Status of your Raspberry (tested on Zero, 2, 3 and 4) to an ST7735S OLED Display.

I use this script to get a quick and up-to-date status of the system every time I walk past my Raspberry Pis.
In this way I can see at a glance the current workload, whether problems are looming and whether the service is currently running.

My Raspberrys are mounted in my 19Rack:
![Raspberry Pis im Rack](https://github.com/Starwhooper/RPi-status-on-OLED/blob/main/examples/raspberrysinrack.jpg)

Please also note my previous solution based on Wireshark 144: https://github.com/Starwhooper/RPi-status-on-OLED
## Example ##

![Display](https://github.com/Starwhooper/RPi-status-on-OLED/blob/main/examples/before_2020-09.png)
![Display](https://github.com/Starwhooper/RPi-status-on-OLED/blob/main/examples/before_2021-06.png)
![Display](https://github.com/Starwhooper/RPi-status-on-OLED/blob/main/examples/newest.png)

## Installation ##
install all needed packages to prepare the software environtent of your Raspberry Pi:

### enable SPI
```bash
sudo sed -i -e 's/#dtparam=spi=on/dtparam=spi=on/g' /boot/config.txt
```

### install required components
```bash
sudo apt install python3-pip git -y
sudo pip3 install luma.lcd json psutil
sudo git clone https://github.com/rm-hull/luma.examples /opt/luma.examples
```

### install this tool itself:
```bash
sudo git clone https://github.com/Starwhooper/RPi-status-via-luma /opt/RPi-status-via-luma
```

### config this tool:
```
sudo cp /opt/RPi-status-via-luma/config.json.example /opt/RPi-status-via-luma/config.json
sudo nano /opt/RPi-status-via-luma/config.json
```
Check https://github.com/Starwhooper/RPi-status-via-luma/wiki/explain-config.json to get more details about the config.json file

### add to autostart ###
add it to rc.local to autostart as boot
```bash
sudo sed -i -e '$i \python3 /opt/RPi-status-via-luma/status.py --rotate 3 --config /opt/luma.examples/conf/st7735.conf &\n' /etc/rc.local
```

## Update ##
If you already use it, feel free to update with
```bash
cd /opt/RPi-status-via-luma
sudo git pull origin main
```

## Hardware ##
### Display ###
I used this 1.8" OLED screen: https://www.az-delivery.de/collections/displays/products/1-8-zoll-spi-tft-display

wires:
* RESET -> GPIO24 = Pin 18
* A0    -> GPIO23 = Pin 16
* LED   -> GPIO18 = Pin 12
* VCC   -> 5V
* GND   -> Ground
* SCK   -> Pin 23
* SDA   -> Pin 19
* CS    -> CE0 = Pin 24

### Case ###
![Display](https://cdn.thingiverse.com/assets/b8/cf/98/25/7c/featured_preview_RPiRack_with_lcd_and_fan.png)
Your can get the STL File and more details regarding the Hardware here: https://www.printables.com/de/model/258934-raspberry-rack-mount-with-lcd-and-fan (thats the previous version, next is comming soon)
