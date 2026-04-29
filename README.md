Prototype 2.0 and rewrite is currently underway with documentation and full build guide. 2.0 will be much closer to a commercial product in terms of build quality, ease of use, and documentation (don't plan to sell just plan for high polish). Now that I have 1.0 done and personally have lived with it for like a year I know what improvements I want. 2.0 will also feature a complete refactor of the code running on the pi as ill move from python to rust. The move to rust will bring massive performance gains (helpful as panel size grows), memory safety as well as inherently more stability, and the refactor will have a lot of code cohesion benefits. 

Prototype 1.0 details (EOL)

Functions as a clock with temperature, phone controllable (shortcut script), brightness adjustable, can play gifs (.ani files), change color of clock, and can get lux and temperature data from another device (I have a esp8266 micropython script in sensors with a lux and temp sensor) meaning it has AUTO BRIGHTNESS.  


RuePanel is a fun project i've worked on which is essentially making my own Divoom panel but better. It has better color reproduction (with caveats), a nice clock presentation, temperature sensoring, IR remote usage instead of an app, and was completely made by me. I sketched, designed, 3D modeled, prototyped, 3D printed, wired, soldered, troubleshooted, and coded EVERYTHING* (couple libraries). I am planning to make it a more generalized and allow for not using certain features, different wiring, and likely different hardware all together. For now I have a lot of plans including making a 32 by 32 version with some advancements. Any and all questions are appreciated. 

EVERYTHING is in beta and expect changes and functionality to be changed/added. 

GIFs
Prototype 1 (16 by 16) most accurate color (current prototype)

![](https://github.com/Mockedarche/RuePanel/blob/main/Media/16by16_example1.gif)

Prototype 1 (16 by 16) functionality (allignment is a video artifact)


![](https://github.com/Mockedarche/RuePanel/blob/main/Media/proto1_example.gif?raw=true)

8 by 8 (first prototype)

![](https://github.com/Mockedarche/RuePanel/blob/main/Media/final_hello_github.gif)

