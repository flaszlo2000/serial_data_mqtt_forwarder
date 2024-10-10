The purpose of this project is to solve one of my issues with Home Assistant where I have multiple devices on a Esp-Now network but I can't add those to Esp-Home because at this moment they are incompatible technologies.

The network looks something like this:  
- (n amount of) Esp using Esp-now as worker device(s) ->  
- Esp using Esp-now as a main (collector) device that forwards the collected data on serial ->  
- This program that reads the collected data and send them to Home Assistant (atm via MQTT)  

Physically this will look like something like this:  
- esp device using somekind of sensor ->
- esp device plugged into raspberry via usb

Reasoning:  
You might ask that why don't I just send the collected data from the main esp device to MQTT.
The reason is simple: I am trying to spare my hardware resources as much as I possibly can.