# Asus Zenfone Splash Editor

A script to build splash.img, which contains the payload to display the boot logo in Asus Zenfone devices..
(A boot logo is the OEM logo displayed when a SoC is booted up)

This tool is created by reverse engineering (lol) and understanding the structure of splash.img from the device's original raw file from the splash partition..

It reads 8 pictures and converts it into sequential RGB24 data (BGR24 actually, in little-endian :wink:), from which each picture can be read individually by the bootloader by reading the splash.img's header (the first 512 bytes).

More Info/Instructions: [XDA Thread](http://forum.xda-developers.com/android/development/guide-how-to-change-boot-logo-splash-t3527347)


Tested and working on the following devices:
Asus Zenfone Selfie
Asus Zenfone 2 Laser

Might also work on other Asus devices, I don't know :bowtie: