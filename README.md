# HP-Agilent-4263B-Option-Unlocker
A script to automatically unlock options 001 and 002 on your HP or Agilent 4263B LCR meter


Install Python and PyVISA, then your choice of Keysight IO Libraries Suite (if using a HPAK USP-GPIB adapter) or National Instruments NI-488.2 software if using an NI GPIB-USB-HS, or whatever respective drivers you need for your GPIB adapter.

It will automatically find and communicate with your 4263B to read the serial number, firmware number, and check if the options are already enabled. (for good measure it'll also tell you if your firmware is out of date).
If you don't have both options enabled, it'll reset the unit and then run self tests to make sure it is all ok (and tell you what errors it finds, if any).
Then it'll generate the option codes, write them into the instrument and finally it will verify the written data.

Once you reboot your instrument, it's all good to go. It's as easy as it could possibly be. It's literally as simple as running the script and letting it do all the work. :)

I have tested it under Windows 10 using an Agilent 83257B USB-GPIB adapter with the Keysight IO Libraries Suite installed, and also a National Instruments GPIB-USB-HS adapter with the NI libraries installed and it works perfectly on both. It should work on any GPIB interfaces that PyVISA supports, let me know how you go with your setup.
(I found the Keysight software 'just works' a bit better with it's auto discovery of connected devices, but once the NI software can see the instrument, it's smooth sailing).


Special thanks to Miek for reverse engineering the checksum magic, and nfmax for providing the commands to read and write to memory!


I have included a clean EPROM dump, just in case. You'll need to change the serial number at the top of the file to match the serial of your unit, which can be acomplished with any decent hex editor.
Firmware version 1.06 is included too, if you need to update to the latest firmware. Just stick the largr EPROM chip in your chip programmer and burn the ROM. No recalibration or other steps required.

eevblog thread: https://www.eevblog.com/forum/testgear/i_ve-got-a-hacking-challenge-for-you-guys!/
