# pylog485 

# About this project #

### What is it ###
This is a python software which installs on a raspberry pi (or any computer). The software logs the data from RS485 (aka modbus) sensors which are connected to the raspberry pi through an RS485 to USB converter. The data is saved locally in an sqlite file. The software sends the data to online databases when there is an internet connection.

The software is a simple django server, installed on the raspberry pi, which can be controlled and configured remotely through a simple webpage that it serves if an internet connection is present. If no internet connection is present then the logged data will be saved in an sqlite database on the raspberry pi. The data is sent to online databases when an internet connection is found.

### Why was it developed ##
The process of reading data from RS485 sensors and sending it to a database is not complex and should not require complex hardware. However, there are currently no cheap solutions in the market to do this, one is forced to purchase an expensive data logger.

### Advantages & disadvantages ###
Compared to a typical datalogger, the advantages are:

* Cheap: about $100 worth of devices is needed for the data logger (excluding the sensors).
* Accurate: working with digital RS485 sensors means that the analogue to digital conversion takes places in the sensor and hence there is no loss of accuracy if sensors are at a distance from raspberry-pi.
* Can connect to many sensors: currently it can connect to 32 RS485 sensors, but with some modifications, this could be increased to 255 sensors.
* Has user-friendly interface: you can connect to the device over the internet from anywhere, view the data, change the settings, update the software, (a simple website is hosted on the device which allows you to control the device).
* Lots of storage capacity: with 8GB memory card, it's no problem to record high resolution data for years in case there is no internet connection.
* Data is sent to a mongodb and to wherever you want: mongodb is a modern database for unstructured data, you can export to csv and other formats. If you would like to send your data to different databases, you have to write code to do this.
* Open source & pythonic: easy to read what is going on and to adapt for your particular case, if you know python...

The disadvantages are:

* You are forced to work with RS485 sensors, 
    * You have less choices of sensors
    * They consumer more power.
    * They are slightly more expensive, for example:
        * The imt solar RS485 sensor (Si-RS485-TC-T, 319,00 €) costs 50 euros more than its analogue equivalent (Si-420TC-T, 269,00 €)
        * The kipp&zonen RS485 pyranometer (SMP 11, 1.995,00€) costs 100 euros more that its analogue equivalent (CMP11 1.895,00 €)
    * note: it is possible to connect to analogue devices by using analogue to digital converters (I havent yet worked on this)
* Needs more power: about 1.5W for raspberry-pi, and 0.5W/sensor, which is much more than an expensive data logger, so you cannot rely on batteries only, you need a power supply or a small PV system.
* Not industrial quality: if you cannot tolerate any hours of missing data, then this might be a problem, I haven't yet heavily tested it, however, I have had the device connected and running for few weeks now without any problems.

# Setting it up #
note: the steps below summarize the steps I took to set it up, there are other ways to do these steps. If you have better ways of implementing certain steps please share them with us! 
* Prepare the SD card as described in the section below
* Make sure the RS458 sensors do not have conflicting addresses
* Plug the wifi adapter to the raspberry pi
* A must if poor or no internet connection is present: plug the real time clock to the rpi  
* Connect wires
    * Connect all the sensors together to the RS485 network, and to the RS485-to-USB converter
    * Connect converter to the raspberry pi through USB
    * Power up the devices
* Make sure that
    * The raspberry pi has access to the internet
* If you installed a real time clock (a real time clock is a must if you do not have stable internet and power supply, because the rpi syncs its time using the internet):
    * Connect with ssh (device ip is `192.168.1.201`)
    * Make sure the system time is correct by executing the command `date` and viewing the time 
    * Copy the system time to the real time clock with `sudo hwclock -w` 
* Port forward
    * optional: If you would like have access to this from outside your local network, in the settings of the router, setup port forwarding to forward a port of your choice to the device 192.168.1.201, at port 9001
* Using another computer that is connected to the same network, open the page that is served by the raspberry pi `http://192.168.1.201:9001` and edit the configuration json string in `http://192.168.1.201:9001/admin/pylog485app/conf/2/` to your needs (login is `pylog485`, password is `pylog485`), see the json string below and the following explanation of it:
    * The `record` process: the software connects to the RS485-to-USB converter using the `rs485_conf`. Every `sample_period` seconds it queries the data using the information in the `sensors_conf` and converts them to the correct scale using `m` and `c`. Every `data_period` seconds it performs the mathematical operation**s** in `pp` on the queried data and saves the results in a local sqlite db in bson format (eg, the configuration belwo gives the following resutls:`{"Tcell-avg": 25.7, "G-avg": 0.0, "Tamb-avg": 23.0, "timestamp": {"$date": 1426423560000}, "G-std": 0.0, "Tmod-avg": 22.03, "Tamb-max": 23.0}`)
    * The `send` process: every `send_period` seconds the software attempts to connect to the database address `mongo_address` and to send the data from the local sqlite db. The software deletes data after `keep_period` seconds from the time the data was sent to the online database
    * The `monitor` process: this uses the GPIO pins to measure voltage and other data to monitor the health of the power system powering the raspberry pi. It is still not completely ready to be used
```
{
    "record": {
        "rs485_conf": {
            "port": "/dev/ttyUSB0",
            "method": "rtu", 
            "baudrate": 9600, 
            "stopbits": 1,
            "bytesize": 8, 
            "parity": "N",
            "retries": 1000, 
            "rtscts": true,
            "timeout": 0.05
         },
        "sample_period": 5,
        "data_period": 60,
        "sensors_conf": {
            "Tamb": {
                "active": true,
                "address": 10,
                "register": 2,
                "pp": ["avg", "max"],
                "m": 0.1,
                "c": -25.0
            },
            "Tmod": {
                "active": true,
                "address": 11,
                "register": 1,
                "pp": ["avg"],
                "m": 0.1,
                "c": -25.0
            },
            "G": {
                "active": true,
                "address": 12,
                "register": 0,
                "pp": ["avg", "std"],
                "m": 1.0,
                "c": 0.0
            },
            "Tcell": {
                "active": true,
                "address": 12,
                "register": 1,
                "pp": ["avg"],
                "m": 0.1,
                "c": -25.0
            }
        }
    },
    "send": {
        "keep_period": 300,
        "send_period": 240,
        "mongo_address": "mongodb://pylog485:pylog485@ds031627.mongolab.com:31627/public"
    },
    "monitor": {
        "gpio_conf": {
            "BatVolt": {
                "active": false,
                "gpio_pin": 4,
                "Vth": 1.551,
                "RC": 3.272,
                "Rratio": 0.01
            }
        },
        "data_period": 60
    }
}
```
* Go to `http://192.168.1.201:9001` and restart all processes (click stop then start) to take into effect the new configuration

# RPI SD card preparation #
* Copy raspbian image to an 8 GB SD card
    * Format the sd card while setting FORMAT SIZE ADJUSTMENT ON using the program https://www.sdcard.org/downloads/formatter_4/eula_windows/
    * Download rasberian image from http://www.raspberrypi.org/downloads/
    * Put the image on the SD card using http://sourceforge.net/projects/win32diskimager/

* Download pylog485 and dependencies on SD card
    * Mount the SD card on the raspberry pi
    * Connect it to the internet with ethernet cable
    * Make sure SSH is enabled (it should be by default) and select finish on the configuration
    * In the configuration, expand the rpi sd card, if you missed the configuration you can find it in `sudo raspi-config`, run the first option
    * Username and password: `pi`, `raspberry`
    * Execute (takes about 25min)`sudo apt-get install git && sudo git clone -b master https://omargammoh@github.com/omargammoh/pylog485.git && sudo apt-get install python-dev <<<y && sudo apt-get install python-pip <<<y && sudo apt-get install tmux && sudo pip install django==1.7 && sudo pip install pymodbus==1.2.0 && sudo pip install pymongo==2.8`

* Setup autologin and autostart    
    * Setup auto login (http://elinux.org/RPi_Debian_Auto_Login)
        * In the file `sudo nano /etc/inittab`
        * Comment the line `1:2345:respawn:/sbin/getty --noclear 38400 tty1`
        * Add under it the line `1:2345:respawn:/bin/login -f pi tty1 </dev/tty1 >/dev/tty1 2>&1` 
    * Run server automatically at log-in
        * Adding at the end of the file `sudo nano /home/pi/.bashrc`
        * The line `. /home/pi/pylog485/start.sh`

* Configure a static-ip wifi (https://kerneldriver.wordpress.com/2012/10/21/configuring-wpa2-using-wpa_supplicant-on-the-raspberry-pi/)
    * note: definitions of things in this link (https://www.modmypi.com/blog/tutorial-how-to-give-your-raspberry-pi-a-static-ip-address)
    * Some documentation (http://www.debian.org/doc/manuals/debian-reference/ch05.en.html#_the_basic_syntax_of_etc_network_interfaces)
    * Edit `sudo nano /etc/wpa_supplicant/wpa_supplicant.conf`
    * To become (with the correct configuration of `ssid` and `psk`, that's your wifi network name and password):

```
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="Your SSID here"
    proto=RSN
    key_mgmt=WPA-PSK
    pairwise=CCMP TKIP
    group=CCMP TKIP
    psk="Your password here"
}    

```
* 
    * Edit `sudo nano /etc/network/interfaces`
    * To become (with the correct configuration of `netmask`, `network` and `gateway`. make sure your router allows for the static ip address `192.168.1.201`, if not then simply choose another address):


```
auto lo
iface lo inet loopback
iface eth0 inet dhcp

#### for a wlan DHCP ip
#iface wlan0 inet dhcp
#   wpa-ssid "xx"
#   wpa-psk "xx"

#### for a wlan static ip
allow-hotplug wlan0
auto wlan0
iface wlan0 inet manual
wpa-roam /etc/wpa_supplicant/wpa_supplicant.conf
iface default inet static
    #the address you want to give your pi, current address can be found with ifconfig, inet addr:192.168.1.4
    address 192.168.1.201
    #from ifconfig, Mask:255.255.255.0
    netmask 255.255.255.0
    #the router IP address, from netstat -nr, Destination 192.168.1.0#
    network 192.168.1.0
    #from netstat -nr, Gateway 192.168.1.1
    gateway 192.168.1.1

```

* Optional but recommended: configure the real time clock,  this needs the RTC hardware (https://www.modmypi.com/blog/installing-the-rasclock-raspberry-pi-real-time-clock)
    * Run `wget http://afterthoughtsoftware.com/files/linux-image-3.6.11-atsw-rtc_1.0_armhf.deb&&sudo dpkg -i linux-image-3.6.11-atsw-rtc_1.0_armhf.deb&&sudo cp /boot/vmlinuz-3.6.11-atsw-rtc+ /boot/kernel.img`
    * Add at the end of the file `sudo nano /etc/modules` the following lines

```
i2c-bcm2708
rtc-pcf2127a
```
* 
  * Add the following lines just before the `exit 0` line in `sudo nano /etc/rc.local`

```
echo pcf2127a 0x51 > /sys/class/i2c-adapter/i2c-1/new_device
( sleep 2; hwclock -s ) &
```
* restart
   * `sudo reboot`

# Usage
* The datalogging and sending of data starts automatically when the raspberry pi boots
* You can log in to the server and control the device by going to `http://192.168.1.201:9001`. If you have port forwarding enabled in your router, you can do this from anywhere with internet access
* The django server is run in a tmux session, login to the raspberry pi thourgh ssh and:
    * run `tmux a -t 0` to see what is being printed, 
    * type `ctrl-b` then `d` to detach tmuw session
    * run `tmux kill-session -t 0` to kill tmux session, this will stop the whole thing 
    * run `. /home/pi/pylog485/start.sh` to run the server in a tmux session 

# TODO:
* Figure out how to log 4..20 mA sensors and 0..10 mV sensors
* Figure out how to monitor 0..30 V signals (to monitor the batter supplying the devices)

# Some usefull linux things
* Restarting the tmux session
    * Kill tmux session with `tmux kill-session -t 0` (replace "0" by session id)
    * Run the server in a tmux session `. /home/pi/pylog485/start.sh`
* Others tmux things
    * A guide on how to use tmux: http://www.hackzine.org/auto-starting-tmux-with-panes-services.html
    * Sharing sessions: http://readystate4.com/2011/01/02/sharing-remote-terminal-session-between-two-users-with-tmux/
    * Session are stored in /tmp
    * `tmux a -t 0` to enter the session with  id "0"
    * `tmux list-sessions`
    * `ctrl-b` then `d` leave the session
* Wifi
    * `sudo ifdown wlan0` to switch off wifi
    * `sudo ifup wlan0` to switch on wifi
    * `ntptime` 
   
* To find the address of the rpi rs485 usb converter
    * `ls -al /dev/ttyUSB* `

* real time clock commands:
    * `hwclock -w to copy the system time into the clock module`
    * `hwclock -r To read the time from the clock module`
    * `hwclock -s To copy the time from the clock module to the system`





# How to test this
* [checked]disconnect one of the sensor while in operation 
    * -> processes continue and data of the sensor should not be logged at all (no NaNs)
    * -> things go back to normal when reconnected
        
* [checked]discconect all sensors
    * -> no data sent to server
    * -> things go back to normal when reconnected
                          
* [checked]disconnect modbus usb
    * -> waits for connection
    * -> things go back to normal when reconnected
    
* disconnect wifi network, disconnect wifi adapter
    * -> [checked]keeps logging
    * -> [checked]things go back to normal when reconnected        

* [checked]turn power off and back on   
* [not good, there is a time delay RTC needed!]start without internet

# Have questions? Need help?
* Contact me on omar dot gammoh at gmail dot com

# Donations
* Bitcoin: `1AkFBf789j1AzV6Hr73fSfBJbihQ7nAKmp`

# Some pics
![alt tag](https://raw.github.com/omargammoh/pylog485/master/img/pylog485.jpg)
![alt tag](https://raw.github.com/omargammoh/pylog485/master/img/website.png)

