import time
import sys
from rpi_ws281x import *
import signal

# LED strip configuration:
LED_COUNT      = 256      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 10     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53


pixel_array = Color(0,0,0) * LED_COUNT

def change_brightness(strip, brightness):
    """Change brightness of the LED strip."""
    strip.setBrightness(brightness)
    strip.show()  # Update the LEDs with the new brightness

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=0):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        
        if wait_ms != 0:
            strip.show()
            time.sleep(wait_ms/1000.0)
    strip.show()


def light_diffuser_test(strip, pixel):
    colors = {
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
        "yellow": (255, 255, 0),
        "orange": (255, 165, 0),
        "purple": (128, 0, 128),
        "pink": (255, 192, 203),
        "cyan": (0, 255, 255),
        "magenta": (255, 0, 255),
        "teal": (0, 128, 128),
        "lime": (0, 255, 0),
        "lavender": (230, 230, 250),
        "brown": (165, 42, 42),
        "maroon": (128, 0, 0),
        "navy": (0, 0, 128),
        "olive": (128, 128, 0),
        "coral": (255, 127, 80),
        "gold": (255, 215, 0),
        "silver": (192, 192, 192),
        "sky blue": (135, 206, 235),
        "violet": (238, 130, 238),
        "turquoise": (64, 224, 208),
        "tan": (210, 180, 140),
        "salmon": (250, 128, 114),
        "indigo": (75, 0, 130)
    }

    change_brightness(strip, 0)
    strip.setPixelColor(pixel, Color(0, 0, 0))
    strip.show()


    for color_name, rgb_values in colors.items():
        for i in range(5, 255, 5):
            change_brightness(strip, i)
            strip.setPixelColor(pixel, Color(*rgb_values))
            strip.show()
            print("Brightness is: " + str(i) + " Color is: " + str(color_name))
            time.sleep(.2)

        


def color_fading_test(strip):
    for i in range(5, 255, 5):
        strip.setPixelColor(0, Color(i, 0, 0))
        strip.setPixelColor(1, Color(0, i, 0))
        strip.setPixelColor(2, Color(0, 0, i))
        strip.show()
        time.sleep(1)


def unique_color_test(strip, pixel):
    colors = {
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
        "yellow": (255, 255, 0),
        "orange": (255, 100, 0),
        "purple": (128, 0, 128),
        "pink": (255, 192, 203),
        "cyan": (0, 255, 255),
        "magenta": (255, 0, 255),
        "teal": (0, 128, 128),
        "lime": (0, 255, 0),
        "lavender": (230, 230, 250),
        "brown": (165, 42, 42),
        "maroon": (128, 0, 0),
        "navy": (0, 0, 128),
        "olive": (128, 128, 0),
        "coral": (255, 127, 80),
        "gold": (255, 215, 0),
        "silver": (192, 192, 192),
        "sky blue": (135, 206, 235),
        "violet": (238, 130, 238),
        "turquoise": (64, 224, 208),
        "tan": (210, 180, 140),
        "salmon": (250, 128, 114),
        "indigo": (75, 0, 130)
    }

    change_brightness(strip, 0)
    strip.setPixelColor(pixel, Color(0, 0, 0))
    strip.show()

    keep_or_not = {}

    for color_name, rgb_values in colors.items():
        for i in range(5, 255, 5):
            change_brightness(strip, i)
            strip.setPixelColor(pixel, Color(*rgb_values))
            strip.show()
            print("Brightness is: " + str(i) + " Color is: " + str(color_name))
            time.sleep(.1)

        keep = input("Keep " + color_name + " or no? t or f: ").lower()

        keep_or_not[color_name] = keep == "t"

    for color, keep_flag in keep_or_not.items():
        print(f"{color}: {keep_flag}")


def color_calibrate(strip, pixel):
    unaltered_colors = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
    "orange": (255, 165, 0),
    "pink": (255, 192, 203),
    "purple": (128, 0, 128),
    "brown": (165, 42, 42),
    "lime": (0, 255, 0),
    "turquoise": (64, 224, 208),
    "gold": (255, 215, 0),
    "silver": (192, 192, 192),
    "maroon": (128, 0, 0),
    "navy": (0, 0, 128),
    "olive": (128, 128, 0),
    "sky blue": (135, 206, 235),
    "violet": (238, 130, 238),
    "tan": (210, 180, 140),
    "salmon": (250, 128, 114),
    "peach": (255, 218, 185),
    "lavender": (230, 230, 250),
    "beige": (245, 245, 220),
    "chartreuse": (127, 255, 0),
    "indigo": (75, 0, 130),
    "khaki": (240, 230, 140),
    "orchid": (218, 112, 214),
    "plum": (221, 160, 221),
    "coral": (255, 127, 80),
    "teal": (0, 128, 128),
    "azure": (240, 255, 255),
    "aquamarine": (127, 255, 212),
    "crimson": (220, 20, 60),
    "firebrick": (178, 34, 34),
    "green yellow": (173, 255, 47),
    "dark orange": (255, 140, 0),
    "light green": (144, 238, 144),
    "dark turquoise": (0, 206, 209),
    "medium purple": (147, 112, 219),
    "dark khaki": (189, 183, 107),
    "hot pink": (255, 105, 180),
    "sandy brown": (244, 164, 96),
    "deep sky blue": (0, 191, 255),
    "medium orchid": (186, 85, 211),
    "pale violet red": (219, 112, 147),
    "rosy brown": (188, 143, 143),
    "spring green": (0, 255, 127),
    "tomato": (255, 99, 71),
    "wheat": (245, 222, 179),
    "yellow green": (154, 205, 50)
    }

    
    colors = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
    "orange": (255, 165, 0),
    "pink": (255, 192, 203),
    "purple": (128, 0, 128),
    "brown": (165, 42, 42),
    "lime": (0, 255, 0),
    "turquoise": (64, 224, 208),
    "gold": (255, 215, 0),
    "silver": (192, 192, 192),
    "maroon": (128, 0, 0),
    "navy": (0, 0, 128),
    "olive": (128, 128, 0),
    "sky blue": (135, 206, 235),
    "violet": (238, 130, 238),
    "tan": (210, 180, 140),
    "salmon": (250, 128, 114),
    "peach": (255, 218, 185),
    "lavender": (230, 230, 250),
    "beige": (245, 245, 220),
    "chartreuse": (127, 255, 0),
    "indigo": (75, 0, 130),
    "khaki": (240, 230, 140),
    "orchid": (218, 112, 214),
    "plum": (221, 160, 221),
    "coral": (255, 127, 80),
    "teal": (0, 128, 128),
    "azure": (240, 255, 255),
    "aquamarine": (127, 255, 212),
    "crimson": (220, 20, 60),
    "firebrick": (178, 34, 34),
    "green yellow": (173, 255, 47),
    "dark orange": (255, 140, 0),
    "light green": (144, 238, 144),
    "dark turquoise": (0, 206, 209),
    "medium purple": (147, 112, 219),
    "dark khaki": (189, 183, 107),
    "hot pink": (255, 105, 180),
    "sandy brown": (244, 164, 96),
    "deep sky blue": (0, 191, 255),
    "medium orchid": (186, 85, 211),
    "pale violet red": (219, 112, 147),
    "rosy brown": (188, 143, 143),
    "spring green": (0, 255, 127),
    "tomato": (255, 99, 71),
    "wheat": (245, 222, 179),
    "yellow green": (154, 205, 50)
    }



    for color_name, rgb_values in colors.items():
        while True:
            print(str(color_name) + ": " + str(rgb_values))
            for i in range(5, 255, 5):
                change_brightness(strip, i)
                r, g, b = colors[color_name]  # Get the current RGB values
                strip.setPixelColor(pixel, Color(r, g, b))  # Set the pixel color with the current RGB values
                strip.show()  # Update the LED strip with the current colors
                #print("Brightness is: " + str(i) + " Color is: " + str(color_name))
                time.sleep(.05)

            change_or_not = input("Change RGB values? y or n: ")
            if change_or_not.lower() == "y":
                r, g, b = colors[color_name]

                print("R: " + str(r))
                print("G: " + str(g))
                print("B: " + str(b))

                which_color = input("Which should change R, G, or B: ")
                how_much = int(input("By how much should it change: "))

                if which_color.lower() == "r":
                    r += how_much
                    if r < 0:
                        r = 0
                elif which_color.lower() == "g":
                    g += how_much
                    if g < 0:
                        g = 0
                elif which_color.lower() == "b":
                    b += how_much
                    if b < 0:
                        b = 0

                colors[color_name] = (r, g, b)
            else:
                break

        print("colors = {\n")
        for i in colors:
            print("\"" + str(i) + "\": (" + ", ".join(str(x) for x in unaltered_colors[i]) + ") | " + "(" + ", ".join(str(x) for x in colors[i]) + "), ")

        print("}")

    print("\n\n")

    for i in colors:
        print("\"" + str(i) + "\": (" + ", ".join(str(x) for x in unaltered_colors[i]) + ") | " + "(" + ", ".join(str(x) for x in colors[i]) + "), ")


def get_color_rgb_load(color_name):
    if color_name == "red":
        return 255, 0, 0
    elif color_name == "green":
        return 0, 255, 0
    elif color_name == "blue":
        return 0, 0, 255
    elif color_name == "black":
        return 0, 0, 0
    elif color_name == "white":
        return 255, 255, 255
    elif color_name == "yellow":
        return 255, 255, 0
    elif color_name == "cyan":
        return 0, 255, 255
    elif color_name == "magenta":
        return 255, 0, 255
    elif color_name == "purple":
        return 128, 0, 128
    elif color_name == "orange":
        return 255, 165, 0
    elif color_name == "pink":
        return 255, 192, 203
    elif color_name == "brown":
        return 165, 42, 42
    elif color_name == "gray":
        return 128, 128, 128
    elif color_name == "light_gray":
        return 192, 192, 192
    elif color_name == "dark_gray":
        return 64, 64, 64
    elif color_name == "olive":
        return 128, 128, 0
    elif color_name == "teal":
        return 0, 128, 128
    elif color_name == "navy":
        return 0, 0, 128
    else:
        # Default to black if an invalid color is provided
        return 0, 0, 0



def color_visiblity_test(strip):
    color_choice = input(
        "Please enter a color from the list. Options are:\nred, green, blue,\nwhite, yellow,\ncyan, magenta, purple,\norange, pink, brown,\ngray, light_gray, dark_gray,\nolive, teal, navy: ")

    wait_time = 0

    r, g, b = get_color_rgb_load(color_choice)

    colorWipe(strip, Color(r, g, b), wait_time)


def itinerary_player(itinerary_file_name, strip, side_length):
    if len(itinerary_file_name) < 4:
        print(("invalid itinerary file"))
        sys.exit(1)

    else:
        extentsion_check = itinerary_file_name[-4:]
        if extentsion_check.lower() != ".iti":
            itinerary_file_name = itinerary_file_name + ".iti"


    with open(itinerary_file_name, 'r') as file:
        line = file.readline()

        while line:
            time_period = line.split()

            file_path = " ".join(time_period[4:])

            time_to_run = int(time_period[0]) - int(time_period[2])

            start_time = time.time()

            print("Should run for: " + str(time_to_run) + " seconds")
            while(time.time() - start_time < time_to_run):
                print("playing file: " + file_path)
                play_animation(strip, file_path, side_length, time.time() + time_to_run)

            print("finished")
            line = file.readline()
            colorWipe(strip, Color(0,0,0), 0)




def play_animation(strip, file_name, side_length, when_to_quit):
    if len(file_name) < 4:
        print("invalid animation file")
        sys.exit(1)
    else:
        extentsion_check = file_name[-4:]
        if extentsion_check.lower() != ".ani":
            file_name = file_name + ".ani"


    with open(file_name, "r") as file:
        line = file.readline()
        while True:
            line = file.readline()
            if "\"" in line:
                line = file.readline()
                break
        fps = line.split().pop()
        length = file.readline()
        kind = file.readline().split()[1]
        length_of_side = int(file.readline().split().pop())

        if length_of_side != side_length:
            print("THIS ANIMATION FILE ISN'T MADE FOR A MATRIX OF THIS SIZE")
            exit()

        print_flag = True
        frames_that_lagged = 0

        fps_interval_ms = 1000.0 / float(fps)

        line = file.readline()
        while line:
            
            start_time = time.time()  # Get the start time
            pixels = line.split(",")
            pixels.pop()
            
            for i in pixels:
                #print(i)
                pixel_details = i.split(" ")
                strip.setPixelColor(int(pixel_details[1]), Color(int(pixel_details[2]), int(pixel_details[3]), int(pixel_details[4])))
                
                
            line = file.readline()
            strip.show()

            if when_to_quit != -1:
                if time.time() >= when_to_quit:
                    return
            
            end_time = time.time()  # Get the end time
            
            duration_ms = (end_time - start_time) * 1000  # Convert duration to milliseconds

            print("Frame took: " + str(duration_ms)  + " / " + str(fps_interval_ms))

            if duration_ms < fps_interval_ms:
                time.sleep((fps_interval_ms - duration_ms) / 1000)  # Convert back to seconds for sleep
            else:
                frames_that_lagged += 1
                if print_flag:
                    print("FRAME TOOK TOO LONG TO PRINT BY: " + str(duration_ms - fps_interval_ms) + " ms")
                    print_flag = False  # Turn off the flag to prevent repetitive printing
                    time.sleep(fps_interval_ms / 1000)  # Sleep for the full FPS interval
                # Continue your existing loop



            
        if kind != "gif":
            colorWipe(strip, Color(0,0,0))
            
        if not print_flag:
            print("There were a total of " + str(frames_that_lagged) + " frames that lagged or took longer to display than the FPS interval")
            
            

    

# Main program logic follows:
if __name__ == '__main__':

    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()

    itinerary_or_ani = input("Is this a .ani file?(Y/N): ")
    is_ani = False

    if itinerary_or_ani.lower() == 'y':
        file_name = input("Please enter the files name or path (with name): ")

        extentsion_check = file_name[-4:]

        if extentsion_check.lower() != ".ani":
            file_name = file_name + ".ani"

        is_ani = True

    else:
        file_name = input("Please enter the files name or path (with name): ")

        extentsion_check = file_name[-4:]

        if extentsion_check.lower() != ".iti":
            file_name = file_name + ".iti"



    
    try:


        change_brightness(strip, 40)
        #color_fading_test(strip)



        if is_ani:
            play_animation(strip, file_name, 16, -1)

        else:
            itinerary_player(file_name, strip, 16)


        colorWipe(strip, Color(0, 0, 0), 10)

        #for i in names_of_files:
            #play_animation(strip, i, 16)
        #color_visiblity_test(strip)
        #light_diffuser_test(strip, 11)
        #colorWipe(strip, Color(255,0,0))
        #unique_color_test(strip, 11)
        #color_calibrate(strip, 11)

    except KeyboardInterrupt:
        print("\nexiting")
        colorWipe(strip, Color(0,0,0), 10)