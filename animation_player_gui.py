import tkinter as tk
import time
import colorsys
import sys
import random
from datetime import datetime, timedelta


"""
Function: rgb_to_hex - takes a given rgb value and correctly formats it for use on the tkinter gui
Expects: Expects that the rgb value is correct and valid
Does: Given a rgb value returns it formatted for tkinter
"""
def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])


"""
Function: create_grid - Using the created canvas it creates the grid that emulates the pixels of our panel (dynamic size)
Expects: Expects the canvas, cell_size, row, and col to all correctly be initialized
Does: Creates the tkinter gui's grid emulating the LED panel
"""
def create_grid(event=None):
    # Clear previous grid items
    canvas.delete("grid")

    # Draw the new grid
    for row in range(rows):
        for col in range(cols):
            color = colors[row][col]
            # Create a rectangle item and add it to the canvas with a tag "grid"
            canvas.create_rectangle(col * cell_size, row * cell_size, (col + 1) * cell_size, (row + 1) * cell_size,
                                     fill=color, outline='black', tags="grid")


"""
Function: color_wipe - Takes a color and wait_ms parameter (defaults to 0) and changes all emulated pixels to be that color
Expects: Expects color_as_hex, canvas, rows, cols to be initialized 
Does: Changes all emulated pixels on the gui to be the given color
"""
def color_wipe(color_as_hex, wait_ms=0):
    for i in range(0, rows):
        for j in range(0, cols):
            colors[i][j] = color_as_hex
            
            if wait_ms != 0:
                create_grid()
                time.sleep(wait_ms/1000.0)
                
    create_grid()
    

"""
Function: get_random_color() - Returns a random color tuple as a HEX
Expects: NONE
Does: Returns a random color tuple as a HEX
"""
def get_random_color():
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
    
    return rgb_to_hex(random.choice(list(colors.values())))


"""
Function: itinerary_player - Simply orchestrates the playing of .ani files in a order and time denotes by the given .ini file
Expects: Expects the emulated panel be correctly initialized as well as the given .ini file be in correct format and pointing to real .ani files
Does: Plays various .ani files denoted by the .ini file onto the emulated LED panel (Tkinter GUI)
"""
def itinerary_player(itinerary_file_name, side_length):
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
                play_animation(file_path, side_length, time.time() + time_to_run)

            print("finished")
            line = file.readline()
            color_wipe(rgb_to_hex((0,0,0)), 0)

def play_animation(file_name, side_length,  when_to_quit):
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
                index = int(pixel_details[1])
                #strip.setPixelColor(int(pixel_details[1]), Color(int(pixel_details[2]), int(pixel_details[3]), int(pixel_details[4])))

                # Calculate row and column indices based on the pattern 
                row = (index % rows)
                col = (index // rows)
                
                if col % 2 != 0:
                    row = translation_map[row]
                     
                     
                #print("Row: " + str(row) + " Col: " + str(col))
                colors[row][col] = (rgb_to_hex((int(pixel_details[2]), int(pixel_details[3]), int(pixel_details[4]))))
                
                
            line = file.readline()
            #strip.show()
            
            create_grid()
            root.update()

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
                    #print_flag = False  # Turn off the flag to prevent repetitive printing
                    time.sleep(fps_interval_ms / 1000)  # Sleep for the full FPS interval
                # Continue your existing loop
            
                
            
        if kind != "gif":
            pass
            #color_wipe(rgb_to_hex(0,0,0))
            
        if not print_flag:
            print("There were a total of " + str(frames_that_lagged) + " frames that lagged or took longer to display than the FPS interval")

"""
Function: temp_test - Emulates the displaying of temperature on the emulated LED panel (Tkinter GUI)
Expects: Expects the tkinter gui, side_length, and temperature be intialized and valid
Does: Displays a given temperature on the emulated LED panel (Tkiner GUI)
"""
def temp_test(side_length, temperature):
    # temperature = 55

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
        [1, 0, 0],
        [1, 0, 0]
    ]

    temperature = str(temperature)
    if len(temperature) >= 3:
        col_offset = 1

    else:
        col_offset = int(side_length / 4) + 1

    row_offset = int(side_length / 2)
    col_count = 0

    for i in range(0, len(temperature)):
        current_matrix = digit_matrices[temperature[i]]
        row_count = row_offset
        for row in current_matrix:
            col_count = col_offset
            for index in row:
                if index == 1:
                    colors[row_count][col_count] = rgb_to_hex((255, 0, 0))
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
                colors[row_count][col_count] = rgb_to_hex((255, 0, 0))
            col_count = col_count + 1

        row_count = row_count + 1


"""
Function: clock_player - Main driver that runs the emulated panels loop. Updates time and temperature on the panel
Expects: file_name, side_length, when_to_quit, rainbow_clock, aswell as the tkinter gui be correctly intiialized
Does: Runs main loop of either playing the .ani or displaying typical clock information with temperature
"""
def clock_player(file_name, side_length, when_to_quit, rainbow_clock):
    temperature = 55
    # Get the current time
    now = datetime.now()

    # Set the time to midnight (00:00)
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Calculate the difference in minutes and convert to an integer
    minutes_since_midnight = int((now - midnight).total_seconds() / 60)

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
        for i in range(0, minutes_since_midnight):
            line = file.readline()

        while line:
            start_time = time.time()  # Get the start time
            pixels = line.split(",")
            pixels.pop()

            for i in pixels:
                pixel_details = i.split(" ")
                index = int(pixel_details[1])

                # Calculate row and column indices based on the pattern
                row = (index % rows)
                col = (index // rows)

                if col % 2 != 0:
                    row = translation_map[row]

                # colors[row][col] = (rgb_to_hex((int(pixel_details[2]), int(pixel_details[3]), int(pixel_details[4]))))

                if rainbow_clock and (
                        int(pixel_details[2]) != 0 or int(pixel_details[3]) != 0 or int(pixel_details[4]) != 0):
                    random_color = get_random_color()
                    colors[row][col] = (random_color)

                else:
                    colors[row][col] = (rgb_to_hex((int(pixel_details[2]), int(pixel_details[3]), int(pixel_details[4]))))

            line = file.readline()
            # strip.show()

            temp_test(side_length, temperature)
            temperature = temperature + 1
            create_grid()

            root.update()

            if when_to_quit != -1:
                if time.time() >= when_to_quit:
                    return

            end_time = time.time()  # Get the end time

            duration_ms = (end_time - start_time) * 1000  # Convert duration to milliseconds

            print("Frame took: " + str(duration_ms) + " / " + str(fps_interval_ms))

            # Get the current time
            now = datetime.now()

            # Calculate the time of the next minute (with seconds and microseconds set to 0)
            next_minute = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)

            # Calculate the difference between now and the next minute
            seconds_until_next_minute = (next_minute - now).total_seconds()

            print(f"Seconds until the next minute: {seconds_until_next_minute}")

            time.sleep(seconds_until_next_minute)

            """
            if duration_ms < fps_interval_ms:
                time.sleep((fps_interval_ms - duration_ms) / 1000)  # Convert back to seconds for sleep

            else:
                frames_that_lagged += 1
                if print_flag:
                    print("FRAME TOOK TOO LONG TO PRINT BY: " + str(duration_ms - fps_interval_ms) + " ms")
                    #print_flag = False  # Turn off the flag to prevent repetitive printing
                    time.sleep(fps_interval_ms / 1000)  # Sleep for the full FPS interval
                # Continue your existing loop
            """



# Set the size of the grid
square_matrix_size = 16
rows = square_matrix_size
cols = square_matrix_size
cell_size = int(720 // square_matrix_size)

# Initialize the colors of each cell
colors = [[rgb_to_hex((255, 255, 255)) for _ in range(cols)] for _ in range(rows)]  # Initialize all cells to white

# Set specific indexes to salmon color
# For example, set cell at row 1, column 2 to salmon

# Create the main window
root = tk.Tk()
root.title("Grid of Colors")

# Create a canvas to draw the grid
canvas = tk.Canvas(root, width=cols * cell_size, height=rows * cell_size)
canvas.pack()

# Draw the initial grid
create_grid()

translation_map = {}

for i in range(0, cols):
    translation_map[i] = (cols - 1) - i

color_wipe(rgb_to_hex((0,0,0)))
try:

    while True:

        #print("Starting animation")
        #play_animation("test", rows, -1)
        clock_player("clock", rows, -1, False)
        #itinerary_player("test", 16)
        color_wipe(rgb_to_hex((0,0,0)))
        sys.exit()

except KeyboardInterrupt:
    print("\nexiting")
    color_wipe(rgb_to_hex((0,0,0)), 20)



# Start the Tkinter event loop
root.mainloop()
