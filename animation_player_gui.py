import tkinter as tk
import time
import colorsys
import sys

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

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


def color_wipe(color_as_hex, wait_ms=0):
    for i in range(0, rows):
        for j in range(0, cols):
            colors[i][j] = color_as_hex
            
            if wait_ms != 0:
                create_grid()
                time.sleep(wait_ms/1000.0)
                
    create_grid()

def play_animation(file_name, side_length):
    with open(file_name + ".ani", "r") as file:
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
                    #print("entered")
                    row = translation_map[row]
                    pass
                     
                     
                #print("Row: " + str(row) + " Col: " + str(col))
                colors[row][col] = (rgb_to_hex((int(pixel_details[2]), int(pixel_details[3]), int(pixel_details[4]))))
                
                
            line = file.readline()
            #strip.show()
            
            create_grid()
            root.update()
            
            end_time = time.time()  # Get the end time
            
            duration_ms = (end_time - start_time) * 1000  # Convert duration to milliseconds

            print("Frame took: " + str(fps_interval_ms) + " / " + str(duration_ms))

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
            pass
            #color_wipe(rgb_to_hex(0,0,0))
            
        if not print_flag:
            print("There were a total of " + str(frames_that_lagged) + " frames that lagged or took longer to display than the FPS interval")
            
            


# Set the size of the grid
square_matrix_size = 8
rows = square_matrix_size
cols = square_matrix_size
cell_size = int(1440 / square_matrix_size) 

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
        
        play_animation("test2", rows)
        color_wipe(rgb_to_hex((0,0,0)))

except KeyboardInterrupt:
    print("\nexiting")
    color_wipe(rgb_to_hex((0,0,0)), 20)



# Start the Tkinter event loop
root.mainloop()
