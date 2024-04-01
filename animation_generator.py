"""
Austin Lunbeck
animation_generator.py

this is a simple python script that creates a .ani file for my LED panel. 
.ani file type supports
full RGB range, comments, FPS, type distinction, only necesary pixel updating (ONPU),
and finally the ability to work with calibrated colors 

Supports 
Taking images from a folder and making them into an .ani
Taking text and converting it to a .ani including color, fps, etc
Taking a gif and converting it to .ani


Future goals
Add a insane amount of various effects (including the ability to customize each)
Taking a video and converting it to .ani
Daily information at a glance with background gif, images, or videos
At a glance panel that will show local temperature, weather, sunrise, sunset, etc

hopefully preview functionality (aka connect to the client and send commands in realtime before finalizing a .ani)

"""
from PIL import Image
import os
import random
import re
import math

square_matrix_size = 8

# Define the dimensions of the image_array
width = square_matrix_size
height = square_matrix_size


"""
variable that holds last frame that was printed (for optimization)
"""
# Create the blanked out image_array filled with black pixels
previous_image_array = [[(0, 0, 0) for _ in range(width)] for _ in range(height)]


"""
Calibration dictionary
"""
calibration_dictionary = None

"""
Color name to RGB values
"""
# color helper function to quickly convert a color's name to it's RGB values (in integers)
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

"""
Calibration
"""
# Function to find the closest color in the calibrated colors dictionary based on RGB values
def find_closest_color(calibrated_colors, r, g, b):
    # Initialize variables
    min_distance = float('inf')
    closest_color = None
    debug = False
    
    # Iterate through calibrated colors
    for color, values in calibrated_colors.items():
        # Unpack original RGB values
        original_rgb = values[0]
        original_r, original_g, original_b = original_rgb
        # Calculate Euclidean distance between original and given RGB values
        distance = math.sqrt((original_r - r) ** 2 + (original_g - g) ** 2 + (original_b - b) ** 2)
        # Update closest color if distance is smaller
        if distance < min_distance:
            min_distance = distance
            closest_color = color
    
    # Optional debug printing
    if debug:
        if closest_color != "black":
            print("Original color RGB: " + str(calibrated_colors[closest_color][0]))
            print("calibrated color RGB: " + str(calibrated_colors[closest_color][1]))

    # Return calibrated RGB values of the closest color
    return calibrated_colors[closest_color][1]


"""
image path/ image to matrix
"""
# take an image's path and convert it to a array of RGB values (or take it's shape as one color) 
def load_image_to_array(image_path_or_frame, color, calibrated_colors):
    """Load an image and convert it to a two-dimensional array of RGB values."""
    
    if not isinstance(image_path_or_frame, Image.Image):
        # Open the image
        image = Image.open(image_path_or_frame)
        # Convert the image to RGB mode (in case it's not already in RGB)
        image = image.convert("RGB")
    else:
        # Convert the image to RGB mode (in case it's not already in RGB)
        image = image_path_or_frame.convert("RGB")
    
    # Get the dimensions of the image
    width, height = image.size
    
    if height != square_matrix_size:
        image = image.resize((square_matrix_size, square_matrix_size), Image.NEAREST)
    
    # Get the dimensions of the image
    width, height = image.size
    
    # Create a two-dimensional array to store the RGB values
    image_array = [[(0, 0, 0) for _ in range(width)] for _ in range(height)]
    
    # Iterate over each pixel and store its RGB values in the array
    for y in range(height):
        for x in range(width):
            r, g, b = image.getpixel((x, y))
            if color is None:
                if calibration_dictionary != None:
                    r, g, b = find_closest_color(calibrated_colors, r, g, b)
                    image_array[y][x] = (r, g, b)
                else:
                    image_array[y][x] = (r, g, b)
            else:
                if r != 0 or g != 0 or b != 0:
                    r, g, b = get_color_rgb_load(color)
                    if calibration_dictionary != None:
                        r, g, b = find_closest_color(calibrated_colors, r, g, b)
                    image_array[y][x] = (r, g, b)
                else:
                    r, g, b = get_color_rgb_load("black")
                    image_array[y][x] = (r, g, b)
    
    return image_array

"""
OUNP - only update necessary pixels 
In short this is the easiest quickest way to drastically (varies a lot on content) reduce both file sizes
but also the amount of pixels to change per frame. Meaning either much larger matrixes can be updated at the same FPS
or much higher FPS can be achieved. 

Potential to improve. Look for ways to remove even more unecessary updates by looking for small changes (unperceptable)
"""
# Function to determine which pixels need to be updated in the animation frame
def only_update_necessary_pixels(previous_image_array, current_image_array):
    # Initialize list to track pixels that need updating
    pixels_to_update = [True for _ in range(square_matrix_size * square_matrix_size)]

    # Iterate over each column of pixels
    for x in range(width):
        # Check if column index is even or odd
        if x % 2 == 0:
            # Iterate over each row of pixels in the column
            for y in range(height):
                # Extract RGB values of current and previous pixels
                r1, g1, b1 = current_image_array[y][x]
                r2, g2, b2 = previous_image_array[y][x]
                # Calculate index of pixel in the flattened array
                index = x * height + y
                # Check if RGB values differ between current and previous pixels
                pixels_to_update[index] = (r1 != r2) or (g1 != g2) or (b1 != b2)
        else:
            # Iterate over each row of pixels in the column in reverse order
            for y in range(height - 1, -1, -1):
                # Extract RGB values of current and previous pixels
                r1, g1, b1 = current_image_array[y][x]
                r2, g2, b2 = previous_image_array[y][x]
                # Calculate index of pixel in the flattened array
                index = x * height + (height - 1 - y)
                # Check if RGB values differ between current and previous pixels
                pixels_to_update[index] = (r1 != r2) or (g1 != g2) or (b1 != b2)

    # Return list indicating which pixels need updating
    return pixels_to_update

"""
Image_array/.ani printer

"""
# takes the image_array (array of a images RGB values) and prints it to the .ani file
def print_frame_to_file(file_name, previous_image_array, current_image_array):
    height = len(current_image_array)
    width = len(current_image_array[0])
    # get what pixels to update from OUNP
    pixels_to_update  = only_update_necessary_pixels(previous_image_array, current_image_array)
    with open(file_name + ".ani", "a") as file:
        file.write(" ")
        for x in range(width):  # Iterate over columns
            if x % 2 == 0:  # Even columns
                for y in range(height):  # Iterate over rows in each column
                    count = x * height + y
                    if pixels_to_update[count]:
                        r1, g1, b1 = current_image_array[y][x]  # Access pixel at (x, y)
                        file.write(f"{count} {r1} {g1} {b1}, ")
                        
            else:  # Odd columns
                for y in range(height - 1, -1, -1):  # Iterate over rows in reverse order
                    count = x * height + (height - 1 - y)
                    if pixels_to_update[count]:
                        r1, g1, b1 = current_image_array[y][x]  # Access pixel at (x, y)
                        file.write(f"{count} {r1} {g1} {b1}, ")
        file.write("\n")


"""
EFFECTS 
"""

"""
falling astroids helpers
"""
def probability_check(numerator, denominator):
    # Generate a random number between 0 and denominator - 1
    random_number = random.randint(0, denominator - 1)
    # Check if the random number falls within the probability range
    return random_number < numerator

def shift_down(matrix):
    # Get the dimensions of the matrix
    rows = len(matrix)
    if rows == 0:
        return matrix  # Empty matrix, no need to shift

    cols = len(matrix[0])

    # Create a new matrix to hold the shifted values
    shifted_matrix = [[(0, 0, 0) for _ in range(cols)] for _ in range(rows)]

    for i in range(rows - 1):
        for j in range(cols):
            shifted_matrix[i + 1][j] = matrix[i][j]

    return shifted_matrix

"""
Falling astroids function
"""
def falling_astroids_effect(length_of_time, frame_rate, file_name, square_matrix_size, calbration_dictionary):
    probability = int(input("Please enter the probability of of 100: "))
    number_of_frames_to_generate = length_of_time * frame_rate
    frame_count = 0
    # Create the blanked out image_array filled with black pixels
    image_array = [[(0, 0, 0) for _ in range(square_matrix_size)] for _ in range(square_matrix_size)]
    # Create the blanked out image_array filled with black pixels
    previous_image_array = [[(0, 0, 0) for _ in range(square_matrix_size)] for _ in range(square_matrix_size)]
    create_new_astroid = False
    non_taken_positions = list(range(square_matrix_size))  # Initialize non_taken_positions

    """
    Generate a frame by making a deep copy of the current frame, checking if any astroids have reached the bottom (if so remove them), 
    shifting down the matrix, then possibly generating a new astroid, finally print the newly generated frame and repeat
    """
    while frame_count < number_of_frames_to_generate:

        previous_image_array = [row[:] for row in image_array]  # Create a deep copy of image_array

        # Reset positions of asteroids that have reached the bottom
        for i in range(square_matrix_size):
            r, g, b = image_array[-1][i]  # Check the last row for each column
            if r != 0 or g != 0 or b != 0:  # If there's an asteroid
                image_array[-1][i] = (0, 0, 0)  # Clear the asteroid
                non_taken_positions.append(i)  # Mark the position as available

        image_array = shift_down(image_array)
        

        create_new_astroid = probability_check(probability, 100)
        if create_new_astroid or not non_taken_positions:  # Check if there are positions available
            if non_taken_positions:  # If there are positions available, create a new asteroid
                position = random.choice(non_taken_positions)
                
                r = random.randint(50, 255)
                g = random.randint(50, 255)
                b = random.randint(50, 255)
                

                if calbration_dictionary != None:
                    (r, g, b) = find_closest_color(calbration_dictionary, r, g, b)

                image_array[0][position] = (r, g, b)
                non_taken_positions.remove(position)
            else:  # If all positions are taken, reset non_taken_positions
                non_taken_positions = list(range(square_matrix_size))

        print_frame_to_file(file_name, previous_image_array, image_array)
        frame_count += 1


"""
Placeholder as realistically need higher pixel panel to make 
"""
def bouncing_ball(length_of_time, frame_rate, file_name, square_matrix_size, calibration_dictionary):
    pass





"""
End effects
"""


"""
GIF helper
"""
# gets the gif's FPS
def get_gif_fps(file_path):
    with Image.open(file_path) as img:
        duration = img.info['duration']  # Get the duration of each frame in milliseconds
        fps = 1000 / duration  # Convert duration from milliseconds to seconds
        return fps
    
# gets the number of frames in a gif
def get_gif_number_of_frames(file_path):
    with Image.open(file_path) as img:
        total_frames = img.n_frames  # Get the total number of frames
        return total_frames


"""
Calibration File Reader
"""
# Function to read calibration data from a file and store it in a dictionary
def read_calibration_file(filename):
    # Initialize an empty dictionary to store color calibration data
    colors = {}
    # Open the calibration file for reading
    with open(filename, "r") as file:
        # Iterate over each line in the file
        for line in file:
            # Extract the color name from the line
            name = line[1:line.rfind('"')]
            # Remove unnecessary characters and split the line into components
            line = line[line.find("(") + 1:]
            line = line.split()
            # Extract original RGB values from the line
            r_original = [int(num) for num in re.findall(r'\d+', line[0])][0]
            g_original = [int(num) for num in re.findall(r'\d+', line[1])][0]
            b_original = [int(num) for num in re.findall(r'\d+', line[2])][0]
            # Extract calibrated RGB values from the line
            r_calibrated = [int(num) for num in re.findall(r'\d+', line[4])][0]
            g_calibrated = [int(num) for num in re.findall(r'\d+', line[5])][0]
            b_calibrated = [int(num) for num in re.findall(r'\d+', line[6])][0]
            # Store the color data in the dictionary
            colors[name] = ((r_original, g_original, b_original), (r_calibrated, g_calibrated, b_calibrated))

    # Return the dictionary containing color calibration data
    return colors



"""
DRIVER

"""
# Check if the file exists
if os.path.exists("calibration.cal"):
    print("here")
    calibration_dictionary = read_calibration_file("calibration.cal")
        
else:
    calibration_dictionary = None


# driver code that determines what type of animation the user wants and then walks them through the selections and creates the .ani file
option = input("Please enter \n1 to convert a folders images to animations\n2 to convert text to animations \n3 to convert a gif \n4 to convert a video"
                + "\n5 Effects \n:")
                
# Create the blanked out image_array filled with black pixels
image_array = [[(0, 0, 0) for _ in range(width)] for _ in range(height)]
# images
if int(option) == 1:
    # Prompt the user for input
    folders_name = input("Please enter the folder's name: ") + "/"
    number_of_pictures = int(input("Please enter the number of frames: "))
    file_name = input("Please enter the name for the output file: ")
    frame_rate = input("Please enter the desired frames per second: ")
    
    # Prepare the file path
    file_path = file_name + ".ani"

    # Remove the file if it already exists
    if os.path.exists(file_path):
        os.remove(file_path)
        print("File deleted successfully.")
    else:
        print("File does not exist.")
    
    # Write animation metadata to the file
    with open(file_name + ".ani", "a") as file:
        file.write("\"\n")
        file.write("\"\n")
        file.write("FPS: " + str(frame_rate) + "\n")
        file.write("Length: " + str(number_of_pictures) + "\n")
        file.write("Type: images\n")
        file.write("Side_Length: " + str(square_matrix_size) + "\n")

    # Iterate over each frame and add it to the animation file
    for i in range(1, int(number_of_pictures) + 1):
        previous_image_array = image_array
        image_array = load_image_to_array(folders_name + str(i) + ".png", None, calibration_dictionary)
        print_frame_to_file(file_name, previous_image_array, image_array)
        
# Text
elif int(option) == 2:
    # Prompt the user for text input
    text = input("Please enter the text you want: ")
    color = input("Please enter a color from the list. Options are:\nred, green, blue,\nblack, white, yellow,\ncyan, magenta, purple,\norange, pink, brown,\ngray, light_gray, dark_gray,\nolive, teal, navy: ")
    file_name = input("Please enter the name for the output file: ")
    frame_rate = input("Please enter the desired frames per second: ")
    
    # Prepare the file path
    file_path = file_name + ".ani"

    # Remove the file if it already exists
    if os.path.exists(file_path):
        os.remove(file_path)
        print("File deleted successfully.")
    else:
        print("File does not exist.")
    
    # Write animation metadata to the file
    with open(file_name + ".ani", "a") as file:
        file.write("\"\n")
        file.write("\"\n")
        file.write("FPS: " + str(frame_rate) + "\n")
        file.write("Length: " + str(len(text)) + "\n")
        file.write("Type: text\n")
        file.write("Side_Length: " + str(square_matrix_size) + "\n")

    # Iterate over each character in the text and add it to the animation file
    for i in text:
        previous_image_array = image_array
        if i.isupper():
            image_array = load_image_to_array("Alphabet/" + str(i) + ".png", color, calibration_dictionary)
            print_frame_to_file(file_name, previous_image_array, image_array)
        elif i.islower():
            image_array = load_image_to_array("Alphabet/" + str(i) + "l" + ".png", color, calibration_dictionary)
            print_frame_to_file(file_name, previous_image_array, image_array)
        elif i.isspace():
            image_array = load_image_to_array("Alphabet/" + "space" + ".png", color, calibration_dictionary)
            print_frame_to_file(file_name, previous_image_array, image_array)

# GIF
elif int(option) == 3:
    # Prompt the user for GIF input
    gif_name = input("Please enter the file name of the gif: ")
    file_name = input("Please enter the output files name: ")
    
    # Get the frames per second from the GIF
    fps = get_gif_fps(gif_name + ".gif")

    # Prepare the file path
    file_path = file_name + ".ani"

    # Remove the file if it already exists
    if os.path.exists(file_path):
        os.remove(file_path)
        print("File deleted successfully.")
    else:
        print("File does not exist.")
        
    # Write animation metadata to the file
    with open(file_name + ".ani", "a") as file:
        file.write("\"\n")
        file.write("\"\n")
        file.write("FPS: " + str(fps) + "\n")
        file.write("Length: " + str(get_gif_number_of_frames(gif_name + ".gif")) + "\n")
        file.write("Type: gif\n")
        file.write("Side_Length: " + str(square_matrix_size) + "\n")
        
    gif = Image.open(gif_name + ".gif")    
    # Iterate over each frame in the GIF and add it to the animation file
    while True:
        try:
            gif.seek(gif.tell() + 1)
        except EOFError:
            break
    
        frame = gif.copy().resize((square_matrix_size, square_matrix_size))
        
        previous_image_array = image_array
        image_array = load_image_to_array(frame, None, calibration_dictionary)
        
        print_frame_to_file(file_name, previous_image_array, image_array)

# Placeholder for video
elif int(option) == 4:
    print("This feature isn't currently implemented")

# Effects
elif int(option) == 5:
    # Prompt the user for effect input
    effect_option = int(input("Select an effect \n1 falling asteroids\n2 bouncing ball\n:"))
    length_of_time = int(input("Length of time for the animation in seconds: "))
    frame_rate = int(input("Desired frame rate: "))
    file_name = input("Please enter the output file name: ")

    # Prepare the file path
    file_path = file_name + ".ani"

    # Remove the file if it already exists
    if os.path.exists(file_path):
        os.remove(file_path)
        print("File deleted successfully.")
    else:
        print("File does not exist.")
        
    # Write animation metadata to the file
    with open(file_name + ".ani", "a") as file:
        file.write("\"\n")
        file.write("\"\n")
        file.write("FPS: " + str(frame_rate) + "\n")
        file.write("Length: " + str(int(frame_rate * length_of_time)) + "\n")
        file.write("Type: effect\n")
        file.write("Side_Length: " + str(square_matrix_size) + "\n")

    if effect_option == 1:
        falling_astroids_effect(length_of_time, frame_rate, file_name, square_matrix_size, calibration_dictionary)
    elif effect_option == 2:
        bouncing_ball(length_of_time, frame_rate, file_name, square_matrix_size, calibration_dictionary)
