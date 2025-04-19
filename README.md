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
Choose one of the two interfaces in depends of the interface of your display. If you have no clue, check out below the chapter about Hardware->Display to know which one you need.
Since Bookworm is not more possible, to enable SPI or I2C Support via command line. Thats means since Debian 12.0, is needed to start
```bash
sudo raspi-config
```
and enable the Interface to SPI or I2C manually.

For pre-bookworm Version, you may go the previous way:
```bash
sudo sed -i -e 's/#dtparam=spi=on/dtparam=spi=on/g' /boot/config.txt
sudo sed -i -e 's/#dtparam=i2c_arm=on/dtparam=i2c_arm=on/g' /boot/config.txt
```
will take effect after next reboot

### install required components
(choose luma.lcd (SPI) or luma.oled (I2C). Or choose booth if you are not sure what you need)
```bash
sudo apt install python3-pip libopenjp2-7 python3-psutil python3-netifaces git -y
sudo apt install python3-luma.lcd
sudo apt install python3-luma.oled
sudo git clone https://github.com/rm-hull/luma.examples /opt/luma.examples
```
#### WaveShare 1.4 Hat
```bash
sudo wget https://raw.githubusercontent.com/Starwhooper/luma.examples/patch-1/conf/st7735_128x128_WShat.conf -O /opt/luma.examples/conf/st7735_128x128_WShat.conf
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

### how to start ###

in case of 1.8" OLED (SPI):
```bash
python3 /opt/RPi-status-via-luma/status.py --rotate 3 --config /opt/luma.examples/conf/st7735.conf
```
in case of 0.91" OLED (I2C):
```bash
python3 /opt/RPi-status-via-luma/status.py --rotate 3  -d ssd1306 --height 32
```
if you get the response _status.py: error: I2C device not found: /dev/i2c-1_ you need to add the parameter --i2c-port 0

in case of 1.44" Waveshare (SPI):
```bash
python3 /opt/RPi-status-via-luma/status.py --rotate 3 --config /opt/luma.examples/conf/st7735_128x128_WShat.conf
```

#### start by service ####
```bash
echo [Unit] | sudo tee -a /etc/systemd/system/rpistatus.service
echo Description=RPi Status via Luma | sudo tee -a /etc/systemd/system/rpistatus.service
echo After=multi-user.target | sudo tee -a /etc/systemd/system/rpistatus.service
echo [Service] | sudo tee -a /etc/systemd/system/rpistatus.service
echo ExecStart=/usr/bin/python3 /opt/RPi-status-via-luma/status.py --rotate 3 --config /opt/luma.examples/conf/st7735.conf | sudo tee -a /etc/systemd/system/rpistatus.service
echo Restart=always | sudo tee -a /etc/systemd/system/rpistatus.service
echo User=root | sudo tee -a /etc/systemd/system/rpistatus.service
echo Group=root | sudo tee -a /etc/systemd/system/rpistatus.service
echo WorkingDirectory=/opt/RPi-status-via-luma | sudo tee -a /etc/systemd/system/rpistatus.service
echo [Install] | sudo tee -a /etc/systemd/system/rpistatus.service
echo WantedBy=multi-user.target | sudo tee -a /etc/systemd/system/rpistatus.service
sudo systemctl enable rpistatus.service
```
(beware to change the ExecStart information as you need)

## Update
If you already use it, feel free to update with
```bash
cd /opt/RPi-status-via-luma
sudo git pull origin main
```

## Hardware
### Displays
i recommend using https://pinout.xyz/# as reverence

#### 1.8" OLED (SPI)
https://www.az-delivery.de/en/products/1-8-zoll-spi-tft-display

connections:
| Display Pin | Raspberry Pin | Raspberry phys. Pin |
|---|---|---|
| LED | GPIO 18 | Pin 12 |
| SCK | SCLK | Pin 23 |
| SDA | MOSI | Pin 19 |
| A0 | GPIO23 | Pin 16 |
| RESET | GPIO24 | Pin 18 |
| CS | CE0 | Pin 24 |
| GND | Ground | Pin 6,9,14,20,25,30,34,39 (only one of them needed) |
| VCC | 5V | Pin 2 and 4 (only one of them needed) |


#### 0.91" OLED (I2C)
https://www.az-delivery.de/en/products/0-91-zoll-i2c-oled-display

connections:
| Display Pin | Raspberry Pin |
|---|---|
| GND | Ground |
| VCC | 3.3V |
| SCL | I2C1 SCL = Pin 5 |
| SDA | I2C1 SDA = Pin 3 |


#### 1.44" Waveshare (SPI)
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
