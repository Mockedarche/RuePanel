import time
import sys
import random
import evdev
from rpi_ws281x import *
from datetime import datetime, timedelta
import requests
import heapq
import socket
import Adafruit_DHT


"""
Function:
Expects:
Does:

"""

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

total_times_queried_temperature = 0

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4


""" 
Function: get_ir_device - Used to initialize the ir device 
Expects: Expects nothing
Does: If the ir device is connected and correctly in the evdev it will return it

"""
def get_ir_device():
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        if (device.name == "gpio_ir_recv"):
            print("Using device", device.path, "n")
            return device
    print("No device found!")

"""
Function: change_brightness - Used to change the brightness of the panel
Expects: Expects that the strip is correctly initialized and that brightness is valid (100 -0) input
Does: Sets the panels brightness to the given brightness value

"""
def change_brightness(strip, brightness):
    """Change brightness of the LED strip."""
    strip.setBrightness(brightness)
    strip.show()  # Update the LEDs with the new brightness

"""
Function: color_wipe - Used to set the entire panel to be 1 color (mostly used to clearing it of color)
Expects: Expects that strip, color, and wait_ms are initialized and or valid input 
Does: Sets the entire panel to the given color doing so pixel by pixel per wait_ms

"""
def color_wipe(strip, color, wait_ms=0):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)

        if wait_ms != 0:
            strip.show()
            time.sleep(wait_ms / 1000)
    strip.show()


"""
Function: itinerary_player - using a ini file it plays various pointed ani files on the panel (following a itinerary dictated)
Expects: Expects the strip to be initialized, itinerary file to correctly be formatted, and side_length to be valid for the given panel
Does: Plays various ani files as dictated by the passed ini file

"""
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



"""
Function: play_animation - plays a given ani file
Expects: Expects the strip to be correctly initialized, file_name to be valid, side_length to be correct for the panel, and when_to_exit to be a multiple of the ani file (if played more than once)
Does:

"""
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
            

"""
Function: rotate_matrix - Given a matrix, and k ( k = // 90 degrees) 
Expects: Expects the matrix to be square and k to be a integer
Does: Rotates the matrix by 90 degrees for EACH K 
"""
def rotate_matrix(matrix, k):
    def rotate_90(matrix):
        # Transpose and then reverse rows to rotate 90 degrees clockwise
        return [list(row) for row in zip(*matrix[::-1])]

    # Reduce k to the equivalent number of rotations (k % 4 because 4 rotations = 360 degrees = original matrix)
    k = k % 4

    for _ in range(k):
        matrix = rotate_90(matrix)

    return matrix


"""
Function: get_color - Returns a tuple from the list of tuples (colors), note list isn't ordered
Expects: Expects index to correctly be within the size of the colors list
Does: Given a index return the corresponding tuple in the colors list
"""
def get_color(index):

    colors = [
        ("red", (255, 0, 0)),
        ("white", (255, 255, 255)),
        ("green", (0, 255, 0)),
        ("blue", (0, 0, 255)),
        ("yellow", (255, 255, 0)),
        ("cyan", (0, 255, 255)),
        ("magenta", (255, 0, 255)),
        ("orange", (255, 165, 0)),
        ("pink", (255, 192, 203)),
        ("purple", (128, 0, 128)),
        ("brown", (165, 42, 42)),
        ("lime", (0, 255, 0)),
        ("turquoise", (64, 224, 208)),
        ("gold", (255, 215, 0)),
        ("silver", (192, 192, 192)),
        ("maroon", (128, 0, 0)),
        ("navy", (0, 0, 128)),
        ("olive", (128, 128, 0)),
        ("sky blue", (135, 206, 235)),
        ("violet", (238, 130, 238)),
        ("tan", (210, 180, 140)),
        ("salmon", (250, 128, 114)),
        ("peach", (255, 218, 185)),
        ("lavender", (230, 230, 250)),
        ("beige", (245, 245, 220)),
        ("chartreuse", (127, 255, 0)),
        ("indigo", (75, 0, 130)),
        ("khaki", (240, 230, 140)),
        ("orchid", (218, 112, 214)),
        ("plum", (221, 160, 221)),
        ("coral", (255, 127, 80)),
        ("teal", (0, 128, 128)),
        ("azure", (240, 255, 255)),
        ("aquamarine", (127, 255, 212)),
        ("crimson", (220, 20, 60)),
        ("firebrick", (178, 34, 34)),
        ("green yellow", (173, 255, 47)),
        ("dark orange", (255, 140, 0)),
        ("light green", (144, 238, 144)),
        ("dark turquoise", (0, 206, 209)),
        ("medium purple", (147, 112, 219)),
        ("dark khaki", (189, 183, 107)),
        ("hot pink", (255, 105, 180)),
        ("sandy brown", (244, 164, 96)),
        ("deep sky blue", (0, 191, 255)),
        ("medium orchid", (186, 85, 211)),
        ("pale violet red", (219, 112, 147)),
        ("rosy brown", (188, 143, 143)),
        ("spring green", (0, 255, 127)),
        ("tomato", (255, 99, 71)),
        ("wheat", (245, 222, 179)),
        ("yellow green", (154, 205, 50))
    ]

    r, g, b = colors[index][1]
    return Color(r, g, b)

"""
Function: add_time_card - simple function just adds a timecard to our heap (thats used to schedule tasks)
Expects: Expects that the time_card_heap has been correctly initialized
Does: Adds the card to the time_card_heap
"""
def add_time_card(when_card_should_be_ran, task_description):
    global time_card_heap
    heapq.heappush(time_card_heap, (when_card_should_be_ran, task_description))



"""
Function: get_weather - Using tomorrow.io's weather api get the current temperature and condition for the given longitude and latitude
Expects: Expects nothing
Does: Returns the current temperature and condition
"""
"""
def get_weather():
    global total_times_queried_temperature
    total_times_queried_temperature += 1
    print("Temperature queried current count: " + str(total_times_queried_temperature))

    # TODO REMOVE BEFORE UPLOADING MAKE SURE TO GET ALL 3
    api_key = "ADD your token here"
    lat = 0
    lon = 0


    url = "https://api.tomorrow.io/v4/timelines"

    params = {
        "location": f"{lat},{lon}",
        "fields": ["temperature", "weatherCode"],
        "timesteps": "current",
        "units": "imperial",
        "apikey": api_key
    }

    # Make the API request
    response = requests.get(url, params=params)
    data = response.json()

    # Extract temperature and weather code
    temperature = data['data']['timelines'][0]['intervals'][0]['values']['temperature']
    weather_code = data['data']['timelines'][0]['intervals'][0]['values']['weatherCode']

    # Round temp to nearest int
    temperature = round(temperature)

    # Map weather code to a description
    weather_conditions = {
        0: "Unknown",
        1000: "Clear",
        1001: "Cloudy",
        1100: "Mostly Clear",
        1101: "Partly Cloudy",
        1102: "Mostly Cloudy",
        2000: "Fog",
        2100: "Light Fog",
        3000: "Light Wind",
        3001: "Wind",
        3002: "Strong Wind",
        4000: "Drizzle",
        4001: "Rain",
        4200: "Light Rain",
        4201: "Heavy Rain",
        5000: "Snow",
        5001: "Flurries",
        5100: "Light Snow",
        5101: "Heavy Snow",
        6000: "Freezing Drizzle",
        6001: "Freezing Rain",
        6200: "Light Freezing Rain",
        6201: "Heavy Freezing Rain",
        7000: "Ice Pellets",
        7101: "Heavy Ice Pellets",
        7102: "Light Ice Pellets",
        8000: "Thunderstorm"
    }

    condition = weather_conditions.get(weather_code, "Unknown")

    return temperature, condition
"""

"""
Function: get_temperature_humidity - uses the DHT22 using the globally scoped sensor and pin variables. Using the DHT22 it gets the temperature (in F) and humidity and returns it
Expects: Expects that the DHT_SENSOR and DHT_PIN is correctly wired to a working DHT22 NOTE catches an error by passing the previous temperature and making humidity 0
Does: Using the DHT22 returns the temperature and humidity if no error occurs. If an error occurs returns previous temperature and humidity as 0
"""
def get_temperature_humidity():
    global temperature


    humidity, new_temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)

    if humidity is not None and new_temperature is not None:
        new_temperature = new_temperature * (9 / 5) + 32.0
        new_temperature = int(new_temperature)
        humidity = int(humidity)
        #print("Returned temperature")
        temperature = new_temperature
        return new_temperature, humidity

    else:
        return temperature, 0




"""
Function: update_temperature_on_panel - Updates the temperature on the panel to current result if enough time has passed
Expects: Expects the strip and translation_map to be correct initialized, side_length, temperature, and desired color to be valid data
Does: Updates the temperature on the panel to what is current given enough time has passed
"""
def update_temperature_on_panel(matrix):
    debug = False

    temperature, humidity = get_temperature_humidity()

    digit_matrices = {
        '0': [
            [1, 1, 1],
            [1, 0, 1],
            [1, 0, 1],
            [1, 0, 1],
            [1, 1, 1]
        ],
        '1': [
            [0, 1, 0],
            [1, 1, 0],
            [0, 1, 0],
            [0, 1, 0],
            [1, 1, 1]
        ],
        '2': [
            [1, 1, 1],
            [0, 0, 1],
            [1, 1, 1],
            [1, 0, 0],
            [1, 1, 1]
        ],
        '3': [
            [1, 1, 1],
            [0, 0, 1],
            [1, 1, 1],
            [0, 0, 1],
            [1, 1, 1]
        ],
        '4': [
            [1, 0, 1],
            [1, 0, 1],
            [1, 1, 1],
            [0, 0, 1],
            [0, 0, 1]
        ],
        '5': [
            [1, 1, 1],
            [1, 0, 0],
            [1, 1, 1],
            [0, 0, 1],
            [1, 1, 1]
        ],
        '6': [
            [1, 1, 1],
            [1, 0, 0],
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1]
        ],
        '7': [
            [1, 1, 1],
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1]
        ],
        '8': [
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1]
        ],
        '9': [
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1],
            [0, 0, 1],
            [1, 1, 1]
        ]
    }

    letter_f_matrix = [
        [1, 1, 1],
        [1, 0, 0],
        [1, 1, 1],
        [1, 0 ,0],
        [1, 0, 0]
    ]

    for row in matrix:
        row[:] = [0] * 16

    temperature = str(temperature)
    if len(temperature) >= 3:
        col_offset = 1

    else:
        col_offset = int(len(matrix) / 4) + 1

    row_offset = int(len(matrix) /2)
    col_count = 0


    for i in range(0, len(temperature)):
        current_matrix = digit_matrices[temperature[i]]
        row_count = row_offset
        for row in current_matrix:
            col_count = col_offset
            for index in row:
                if index == 1:
                    matrix[row_count][col_count] = 1
                col_count = col_count + 1

            row_count = row_count + 1
        col_offset = col_count + 1

    current_matrix = letter_f_matrix
    row_count = row_offset
    col_offset = col_count + 1

    for row in current_matrix:
        col_count = col_offset
        for index in row:
            if index == 1:
                matrix[row_count][col_count] = 1
            col_count = col_count + 1

        row_count = row_count + 1

    if debug:
        print("Completed temperature frame")

    # Add the time_card for when to update time again
    current_time = datetime.now()

    time_to_add = timedelta(seconds=10)

    time_to_update = current_time + time_to_add

    add_time_card(time_to_update, "Temperature")

    return matrix

"""
Function update_time_on_panel - takes the given matrix that holds the time and updates it to hold the current time
Expects: Expects that matrix is intialized and of the correct size 
Does: Updates the time on the given matrix
"""
def update_time_on_panel(matrix):
    debug = False

    # Get the current time
    now = datetime.now()

    # Format the time as "h:mm" (12-hour format without AM/PM)
    time_str = now.strftime("%-I:%M")

    digit_matrices = {
        '0': [
            [1, 1, 1],
            [1, 0, 1],
            [1, 0, 1],
            [1, 0, 1],
            [1, 1, 1]
        ],
        '1': [
            [0, 1, 0],
            [0, 1, 0],
            [0, 1, 0],
            [0, 1, 0],
            [0, 1, 0]
        ],
        '2': [
            [1, 1, 1],
            [0, 0, 1],
            [1, 1, 1],
            [1, 0, 0],
            [1, 1, 1]
        ],
        '3': [
            [1, 1, 1],
            [0, 0, 1],
            [1, 1, 1],
            [0, 0, 1],
            [1, 1, 1]
        ],
        '4': [
            [1, 0, 1],
            [1, 0, 1],
            [1, 1, 1],
            [0, 0, 1],
            [0, 0, 1]
        ],
        '5': [
            [1, 1, 1],
            [1, 0, 0],
            [1, 1, 1],
            [0, 0, 1],
            [1, 1, 1]
        ],
        '6': [
            [1, 1, 1],
            [1, 0, 0],
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1]
        ],
        '7': [
            [1, 1, 1],
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1]
        ],
        '8': [
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1]
        ],
        '9': [
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1],
            [0, 0, 1],
            [1, 1, 1]
        ],
        ':': [
            [0, 0],  # First row (top)
            [0, 1],  # Second row (middle)
            [0, 0],  # Third row (space)
            [1, 0],  # Fourth row (bottom dot)
            [0, 0]  # Fifth row
        ]
    }

    for row in matrix:
        row[:] = [0] * 16

    time_str = str(time_str)
    col_offset = 0
    row_offset = 0
    col_count = 0
    spacing_count = 0
    if len(time_str) == 4:
        spacing_count += 1
        col_offset += 3

    for i in range(0, len(time_str)):
        if spacing_count == 1 or spacing_count == 4:
            col_offset += 1
        current_matrix = digit_matrices[time_str[i]]
        row_count = row_offset
        for row in current_matrix:
            col_count = col_offset
            for index in row:
                if index == 1:
                    if debug:
                        print("Row_count " + str(row_count) + " Col_count " + str(col_count))
                    matrix[row_count][col_count] = 1

                col_count = col_count + 1

            row_count = row_count + 1
        col_offset = col_count
        spacing_count += 1

    current_time = datetime.now()

    # Create a new datetime object for the next minute
    if current_time.second == 0:
        time_to_update = current_time + timedelta(minutes=1)
    else:
        time_to_update = current_time.replace(second=0, microsecond=0) + timedelta(minutes=1)

    add_time_card(time_to_update, "Time")

    if debug:
        print("Completed time frame")

    return matrix


"""
Function/helper: helper_is_black - returns if a passed color is black
Expects: Expects nothing
Does: returns if a passed color is black

"""
def helper_is_black(color):
    return color == 0x000000

"""
Function: change_clocks_color - Simply changes the strips color (goes through the entire strip and changes all non black colors to the desired color_
Expects: Expects strip and desired_color to be correctly initializaed 
Does: Changes all the pixels on the strip that aren't black to the desired color

"""
def change_clocks_color(strip, desired_color):
    for i in range(strip.numPixels()):
        color = strip.getPixelColor(i)
        if not helper_is_black(color):
            strip.setPixelColor(i, desired_color)

    strip.show()

"""
Function: compositor - functions as a typical compositor would. AKA Laying multiple images (matrixes) onto a display (strip)
Expects: Expects strip, matrixes, translation_map, and the desired color be correctly intialized 
Does: Compsites the panel using multiple matrixes, translation_map (matrix to strip), and the desired color
"""
def compositor(strip, matrixes, translation_map, desired_color):
    debug = False

    color_black = Color(0,0,0)
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color_black)

    if debug:
        print(matrixes)
        print("\n\n\n\n")
        print(translation_map)
        print("\n\n\n\n")
    for matrix in matrixes:
        row_count = 0
        col_count = 0
        for row in matrix:
            for element in row:
                if debug:
                    print("Row_count " + str(row_count) + " Col_count " + str(col_count))
                    print("Accessing pixel " + str(translation_map[row_count][col_count]))

                if element == 1:
                    if debug:
                        print("true")
                    strip.setPixelColor(translation_map[row_count][col_count], desired_color)
                elif element != 0:
                    strip.setPixelColor(translation_map[row_count][col_count], element)

                col_count += 1

            col_count = 0
            row_count += 1


    strip.show()



"""
Function: clock_player - Handles all tasks related to the clock behavior of the panel (time, temperature, brightness, etc)
Expects: Expects strip to be correctly initialized and side_length to be valid
Does: Sets up and updates the clock to display the current time and temperature while accepting user IR commands for brightness etc

"""
def clock_player(strip, side_length, time_card_heap):
    global brightness
    desired_color = Color(255, 0, 0)
    color_position = 0
    
    # Get the current time
    now = datetime.now()

    # Set the time to midnight (00:00)
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Calculate the difference in minutes and convert to an integer
    minutes_since_midnight = int((now - midnight).total_seconds() / 60)

    translation_map = [[0 for _ in range(side_length)] for _ in range(side_length)]

    rows = len(translation_map)
    cols = len(translation_map[0])  # Assuming the matrix is not empty
    count = 0

    for col in range(cols):
        if col % 2 == 0:
            # Traverse down for even-numbered columns
            for row in range(rows):
                translation_map[row][col] = count
                count = count + 1
        else:
            # Traverse up for odd-numbered columns
            for row in range(rows - 1, -1, -1):
                translation_map[row][col] = count
                count = count + 1

    translation_map = rotate_matrix(translation_map, 3)
    num_rows = 16
    num_cols = 16
    matrixes = []
    time_matrix = [[0 for _ in range(num_cols)] for _ in range(num_rows)]
    temperature_matrix = [[0 for _ in range(num_cols)] for _ in range(num_rows)]
    update_time_on_panel(time_matrix)
    matrixes.append(time_matrix)
    update_temperature_on_panel(temperature_matrix)
    matrixes.append(temperature_matrix)
    compositor(strip, matrixes, translation_map, desired_color)


    while(True):
        current_time = datetime.now()
        if time_card_heap:
            first_task_time, first_task_description = time_card_heap[0]

            # time to do a task
            if first_task_time <= current_time:
                heapq.heappop(time_card_heap)
                print("running task " + first_task_description)

                if first_task_description == "Time":
                    matrixes[0] = update_time_on_panel(time_matrix)
                    compositor(strip, matrixes, translation_map, desired_color)
                elif first_task_description == "Temperature":
                    matrixes[1] = update_temperature_on_panel(temperature_matrix)
                    compositor(strip, matrixes, translation_map, desired_color)
                else:
                    print("Invalid desired task no task called " + first_task_description)

        event = dev.read_one()
        if (event):
            print("Received commands", event.value)
            # Turn brightness up
            if event.value == 9:
                if brightness < 35:
                    change_brightness(strip, (brightness + 1))
                    brightness += 1
                    print("Changed Brightness to " + str(brightness))

            # Turn brightness down
            elif event.value == 7:
                if brightness > 1:
                    change_brightness(strip, (brightness - 1))
                    brightness -= 1
                    print("Changed Brightness to " + str(brightness))

            # Turn off the light
            elif event.value == 69:
                change_brightness(strip, 0)
                brightness = 0
                print("Changed Brightness to " + str(brightness))

            # Change the panels color up 1 position
            elif event.value == 67:
                if color_position < 51:
                    color_position += 1
                    desired_color = get_color(color_position)
                    compositor(strip, matrixes, translation_map, desired_color)

            # Change the panels color down a position
            elif event.value == 68:
                if color_position > 0:
                    color_position -= 1
                    desired_color = get_color(color_position)
                    compositor(strip, matrixes, translation_map, desired_color)

        time.sleep(0.0166)





"""
Driver:
Expects: NONE
Does: Sets up ir_device, strip, etc for the panel to function

"""
if __name__ == '__main__':

    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()

    global brightness
    global dev
    global time_card_heap
    global temperature

    temperature = 10

    dev = get_ir_device()

    #brightness = int(input("Please enter the desired brightness (max 35): "))

    time_card_heap = []


    brightness = 35


    # 35 max
    change_brightness(strip, brightness)
    clock_player(strip, 16, time_card_heap)

    if brightness > 35:
        brightness = 35
    elif brightness <= 0:
        brightness = 1

    color_wipe(strip, Color(0,0,0), 1)

    itinerary_or_ani_or_clock = input("Is this a .ani file?(A), or a .iti file?(I), or play clock (C): ")
    is_ani = False
    is_iti = False
    is_clock = False

    if itinerary_or_ani_or_clock.lower() == 'a':
        file_name = input("Please enter the files name or path (with name): ")

        extentsion_check = file_name[-4:]

        if extentsion_check.lower() != ".ani":
            file_name = file_name + ".ani"

        is_ani = True

    elif itinerary_or_ani_or_clock.lower() == 'i':
        file_name = input("Please enter the files name or path (with name): ")

        extentsion_check = file_name[-4:]

        if extentsion_check.lower() != ".iti":
            file_name = file_name + ".iti"
            
        is_iti = True
    
    else:
        is_clock = True


    while True:
    
        try:

            # 35 max
            change_brightness(strip, brightness)

            if is_ani:
                play_animation(strip, file_name, 16, -1)

            elif is_iti:
                itinerary_player(file_name, strip, 16)
            elif is_clock:

                clock_player(strip, 16, time_card_heap)

        except KeyboardInterrupt:
            print("\nexiting")
            color_wipe(strip, Color(0,0,0), .5)
            break
            
    
    #colorWipe(strip, Color(0, 0, 0), 10)