# RPi-status-via-luma #

To provide the Status of your Raspberry tested on Zero, Zero 2, 2, 3 and 4) to an ST7735S OLED Display. If you use a Wireshark 1.44", please note my previous solution: https://github.com/Starwhooper/RPi-status-on-OLED

I use this script to get a quick and up-to-date status of the system every time I walk past my Raspberry Pis.
In this way I can see at a glance the current workload, whether problems are looming and whether the service is currently running.

My Raspberrys prepared to mounted in my 19Rack:
![Raspberry Pis in 19" rack](https://github.com/Starwhooper/RPi-status-via-luma/blob/main/pictures/somerpisinrack.webp)
![Front of a common enclosure](https://github.com/Starwhooper/RPi-status-via-luma/blob/main/pictures/commonfront.webp)

## Installation
install all needed packages to prepare the software environtent of your Raspberry Pi:

### enable SPI or I2C
Choose one of the two interfaces in depends of the interface of your display. If you have no clue, check out below the chapter about ![Hardware](https://github.com/Starwhooper/RPi-status-via-luma/edit/main/README.md#hardware) -> Display to know which interface your display need.

#### enable spi on trixi:
```bash
sudo raspi-config nonint do_spi 0
````
#### enable i2c on trixi:
```bash
sudo raspi-config nonint do_i2c 0
````
#### enable spi or i2c on bookworm:
```bash
sudo raspi-config
```
and enable the Interface to SPI or I2C manually.
#### enable spi on earlier versions:
```bash
sudo sed -i -e 's/#dtparam=spi=on/dtparam=spi=on/g' /boot/config.txt
```
#### enable i2c on earlier versions:
```bash
sudo sed -i -e 's/#dtparam=i2c_arm=on/dtparam=i2c_arm=on/g' /boot/config.txt
```

all of it will take effect after next reboot
```bash
sudo reboot
```


### install required components
install python 3 components, [luma with examples](https://github.com/rm-hull/luma.examples) and more.
(choose luma.lcd (SPI) or luma.oled (I2C). Or choose booth if you are not sure what you need)
```bash
sudo apt install python3-pip libopenjp2-7 python3-psutil python3-netifaces git -y
sudo apt install python3-luma.lcd
sudo apt install python3-luma.oled
sudo git clone https://github.com/rm-hull/luma.examples /opt/luma.examples
```
#### WaveShare 1.4 Hat
in case of a WareShare 1.4 hat, its nessesary to add a additonal configurationfile to luma
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

#### to start as service ####
```bash
sudo wget https://raw.githubusercontent.com/Starwhooper/RPi-status-via-luma/blob/main/create%20service/rpistatus.service -O /etc/systemd/system/rpistatus.service
sudo systemctl enable rpistatus.service
```
(beware to change the ExecStart information as you need)

## Update
If you already use it, feel free to update with
```bash
cd /opt/RPi-status-via-luma
sudo git reset --hard #online nessesary if you changed the local code meanwhile
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
![Display](https://media.printables.com/media/prints/300085/stls/2713235_9723117c-592d-490b-b367-599f8e6dbcb8/thumbs/cover/320x240/png/rpi3_fan_sd_18display-v20221107_preview.webp)
Your can get the openSCAD or STL File and more details regarding the Hardware here: https://www.printables.com/de/model/300085 
