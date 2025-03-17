# DIY-Emu-Black-Dash-Rpi5-V2

![Working Dash](https://github.com/valtsu23/Pictures/blob/main/DIY-Emu-Black-Dash/IMG_20240612_141538698.jpg)

Raspberry Pi based digital dash working with Ecumaster Emu Black. 
Based on https://github.com/valtsu23/DIY-Emu-Black-Dash.
This version only works on Raspberry Pi 5 and supports multiple screen resolutions

### Version history

### To do
- Update pictures
- More testing
- SMD pcb for sale (maybe some day)

### Additional data
  - [Video](https://youtu.be/x8BvJFvcHbc) 
  - [Raspberry Pi 5 setup guide](https://drive.google.com/file/d/1I3_qu0iXsNpiGuRe7i7J77W4oreEQuEp/view?usp=sharing)
  - [Case and pcb files](https://drive.google.com/file/d/1F2OR0nffseqO3x1aVwaf4AkE6jhCyLvB/view?usp=sharing) (Used software: FreeCAD and Fusion 360)
  - [Pcb schematic in pdf](https://drive.google.com/file/d/1KawKwaSzzWXQF_xuIObFZ1UPyJIFHP33/view?usp=drive_link)

### Technical specs:
- Raspberry Pi 5 Model B 4GB (will work even with all Rpi 5 version)
- Raspberry Pi Active Cooler
- Raspberry Pi RTC Battery
- SanDisk Extreme Pro UHS-I U3 64GB microSD
- 5" sunlight readable display with touchscreen from Makerplane:
  - https://store.makerplane.org/5-sunlight-readable-touchscreen-hdmi-display-for-raspberry-pi/
- DIY PCB inside the enclosure

### Hardware features
Raspberry Pi 5 handles the communicatin with all the hardware via SPI and I2C. Can bus communication with MCP2515, ADC (MCP3002) reads light sensor values and Raspberry Pi adjusts screen brightness based on ambient light. On board RTC to keep the clock in time. Neopixels for shiftlight. 12v to 5v DC-DC converter on board. Device needs switched 12V and continous 12v from battery to work correctly. Continous power is connected to a relay on PCB. Switched power wakes up the device and Raspberry pi starts booting and relay turns on. When Can Bus stream is lost Raspberry Pi automatically starts shutdown process. After shutdown the relay turns off and cuts power from the device. The device doesn't consume any power after shutdown. Small button as a failsafe if Raspberry Pi crashes (pressing thins buttons turns relay off). 

### Support for different screens
Basically any hdmi screen can be used, but aspect ratio should be close to 16 : 9. Tested on these resolutions: 1920x1080, 1280x720, 800x480.  
I think touchscreen should work with most of the displays. Also the screen brightness control only works on Makerplane screen. 

### Software specs
- Raspberry Pi OS Lite 64bit (Bookworm)
  - Python code runs from command line without a windows manager
  - Gauge cluster software is based on Pygame graphics library
### Performance
  - Boot time  is about 15s
  - I have made a lot of work to make the program light as possible
  - Only part of the screen is updated when needed, not the whole screen (this helps for cpu load)
### Graphic software functions
- There is 6 sensors data (3 left and 3 right) that you can choose to display with touscreen
- Bar on the bottom of the screen in normal situation is blue and shows Raspberry pi CPU temperature and CPU load
- If there is some error detected by ECU or battery voltage is low. Error flags are shown on the bottom of the screen and the bar is red. 

### Can bus stream
- Most of the data needed is read from Ecumaster Emu Black can stream
- There is also DIY can bus device sending message id 0x400, which contains
  - Turn signals
  - High beam on
  - Fuel level
  - Ambient temperature

### Case
- Designed for Rpi4 and Rpi5
- Designed with FreeCAD
- Filament is PETG
- M3x6 machine screws 2 pcs
- M4 thread insert 1 pcs
- M4x8 machine screw 1pcs
- M4x20 machine screw 2pcs
- M4 nut 2pcs

### Parts for PCB
#### From www.partco.fi/en
  - MCP3002-I/P
  - 3A diode 
  - 1A diode 2pcs
  - P6KE18A transient diode (for overvoltage protection)
  - 15pF Ceramic capacitor 2pcs
  - 16Mhz crystal
  - BPW42 3mm phototransistor or similar
  - 2N3904 NPN transistor or similar
  - B3F-31XX Omron switch or SKH KKK 2 from partco.fi
  - 120 0,6w resistor
  - 10K 0,6w resistor
  - 2K2 0,6w resistor
  - 1M 0,6w resistor 
  - 1x40 male pin header
  - 0,22mm2 - 0,5mm2 wires (0,5mm2 recommended for power and ground)
  - MCP2515-I/P
  - MCP2562-E/P
  - IC SOCKET 18-PINS (optional)
  - IC SOCKET 8-PINS 2pcs (optional)
  - FTR-F3AA005V
#### From partco.fi, when using a PCB designed for Makerplane display
  - 2x13 male pin header with long pins (20mm total length)
  - 2x13 female smd pin header
#### From tme.eu, when using a Hat PCB on top of Raspberry Pi
  - 2x20 female pin header with long pins SSQ-120-03-T-D
  - M2.5 screw spacer 16mm 222X16DREMEC 4pcs
  - M2.5x6 countersunk screw 4pcs
  - M2.5 nuts 4pcs
#### From www.Berrybase.de
  - NeoPixel Stick mit 8 WS2812 5050 RGB LEDs (Copy of Adafruit's product. Dimensions won't match)
#### From www.botland.store/
  - Pololu Step-Down Voltage Converter D24V22F5 - 5V 2,5A 2858
#### From www.ebay.com
  - 5pin JST-SM connector pair

### Pictures with Raspberry Pi 4, DS3231 (not needed) and makerplane Display
![Alt PCB](https://github.com/valtsu23/Pictures/blob/main/DIY-Emu-Black-Dash/IMG_20240528_233423409.jpg)

![Alt Inside](https://github.com/valtsu23/Pictures/blob/main/DIY-Emu-Black-Dash/IMG_20240528_234437181.jpg)

![Alt Case1](https://github.com/valtsu23/Pictures/blob/main/DIY-Emu-Black-Dash/IMG_20240528_234606426.jpg)

![Alt Case2](https://github.com/valtsu23/Pictures/blob/main/DIY-Emu-Black-Dash/IMG_20240528_234642311.jpg)

![Alt Case3](https://github.com/valtsu23/Pictures/blob/main/DIY-Emu-Black-Dash/IMG_20240528_234623667.jpg)

### Here is a Hat PCB that is designed to work with any display. Functions are the same. There is also connector for Raspberry Pi touch 2 display power. 
![Alt Hat PCB](https://github.com/valtsu23/Pictures/blob/main/DIY-Emu-Black-Dash/IMG_20250207_003403716.jpg)

![Alt Hat PCB](https://github.com/valtsu23/Pictures/blob/main/DIY-Emu-Black-Dash/IMG_20250207_003448921.jpg)
