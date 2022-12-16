# RPi-status-via-luma #

To provide the Status of your Raspberry (tested on Zero, 2, 3 and 4) to an ST7735S OLED Display.

I use this script to get a quick and up-to-date status of the system every time I walk past my Raspberry Pis.
In this way I can see at a glance the current workload, whether problems are looming and whether the service is currently running.

My Raspberrys prepared to mounted in my 19Rack:
![Raspberry Pis im Rack](https://media.printables.com/media/prints/300085/images/2715870_a53f284c-180c-4feb-9401-bd60474f65ca/thumbs/inside/1920x1440/jpg/img20221108094538.webp)

Please also note my previous solution based on Wireshark 144: https://github.com/Starwhooper/RPi-status-on-OLED

## Installation
install all needed packages to prepare the software environtent of your Raspberry Pi:

### enable SPI or I2C
(choose one of the two commands in depends of the interface of your display)
```bash
sudo sed -i -e 's/#dtparam=spi=on/dtparam=spi=on/g' /boot/config.txt
sudo sed -i -e 's/#dtparam=i2c_arm=on/dtparam=i2c_arm=on/g' /boot/config.txt
```
will take effect after next reboot

### install required components
(choose luma.lcd (SPI) or luma.oled (I2C). Or choose booth if you are not sure what you need)
```bash
sudo apt install python3-pip libopenjp2-7 python3-psutil python3-netifaces git -y
sudo pip3 install luma.lcd
sudo pip3 install luma.oled
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
in case of 1.8" OLED:
```bash
sudo sed -i -e '$i \python3 /opt/RPi-status-via-luma/status.py --rotate 3 --config /opt/luma.examples/conf/st7735.conf &\n' /etc/rc.local
```
in case of 0.91" OLED:
```bash
sudo sed -i -e '$i \python3 /opt/RPi-status-via-luma/status.py  -d ssd1306 --height 32 &\n' /etc/rc.local
```

in case of 1.44" Waveshare:
```bash
sudo sed -i -e '$i \python3 /opt/RPi-status-via-luma/status.py --rotate 3 --config /opt/luma.examples/conf/st7735_128x128.conf &\n' /etc/rc.local
```

## Update
If you already use it, feel free to update with
```bash
cd /opt/RPi-status-via-luma
sudo git pull origin main
```

## Hardware
### Displays
i recommend using https://pinout.xyz/# as reverence

#### 1.8" OLED
https://www.az-delivery.de/en/products/1-8-zoll-spi-tft-display

connections:
| Display Pin | Raspberry Pin |
|---|---|
| LED | GPIO 18 = Pin 12 |
| SCK | Pin 23 |
| SDA | Pin 19 |
| A0 | GPIO23 = Pin 16 |
| RESET | GPIO24 = Pin 18 |
| CS | CE0 = Pin 24 |
| GND | Ground |
| VCC | 5V |


#### 0.91" OLED
https://www.az-delivery.de/en/products/0-91-zoll-i2c-oled-display

connections:
| Display Pin | Raspberry Pin |
|---|---|
| GND | Ground |
| VCC | 3.3V |
| SCL | I2C1 SCL = Pin 5 |
| SDA | I2C1 SDA = Pin 3 |


#### 1.44" Waveshare
https://www.waveshare.com/wiki/1.44inch_LCD_HAT

connections:
| Display Pin | Raspberry Pin |
|---|---|
| Display Pin 1 | Raspberry 3.3V |
| Display Pin 6 | Raspberry Ground Pin |
| Display **Pin 13** | Raspberry **Pin 18** |
| Display Pin 19 | Raspberry Pin 19 |
| Display **Pin 22** | Raspberry **Pin 16** |
| Display Pin 23 | Raspberry Pin 23 |
| Display Pin 24 | Raspberry Pin 24 |


### Case ###
![Display](https://cdn.thingiverse.com/assets/b8/cf/98/25/7c/featured_preview_RPiRack_with_lcd_and_fan.png)

Your can get the openSCAD or STL File and more details regarding the Hardware here: https://www.printables.com/de/model/300085 
