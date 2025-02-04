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


"""
from PIL import Image, ImageSequence
import os
import random
import re
import math
import numpy as np


square_matrix_size = 16

# Define the dimensions of the image_array
width = square_matrix_size
height = square_matrix_size

# Defines the amount to rotate the frame before printing NOTE hard coded and expected to be included in device registration
# 3 is used for wall
rotate_k = 3


"""
variable that holds last frame that was printed (for optimization)
"""
# Create the blanked out image_array filled with black pixels
previous_image_array = [[(0, 0, 0) for _ in range(width)] for _ in range(height)]


"""
Holds general colors for quick more satisfying color selection
"""
primary_colors = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "yellow": (255, 255, 0),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
    "purple": (128, 0, 128),
    "orange": (255, 165, 0),
    "pink": (255, 192, 203),
    "brown": (165, 42, 42),
    "gray": (128, 128, 128),
    "light_gray": (192, 192, 192),
    "dark_gray": (64, 64, 64),
    "olive": (128, 128, 0),
    "teal": (0, 128, 128),
    "navy": (0, 0, 128)
}

# picks a random color from our primary color and if calibration dictionary is initialized it calibrates the color and returns it else just returns it
"""
Function_Helper: pick_random_color - Helper function to quickly pick a random color from the primary_color dictionary
Expects: primary_colors be correctly intialized
Does: Returns a random element from primary_colors

"""
def pick_random_color():
    color_name = random.choice(list(primary_colors.keys()))

    if calibration_dictionary != None:
        #print("cal wasn't none")
        r, g, b = primary_colors[color_name]
        return find_closest_color(calibration_dictionary, r, g, b)

    return primary_colors[color_name]


"""
Calibration dictionary
"""
calibration_dictionary = None

"""
Color name to RGB values
"""
"""
Function_Helper: get_color_rgb_load recieves a colors name and quickly returns a tuple containing its RGB values
Expects: None
Does: Returns the color_names corresponding RGB values as a tuple

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
"""
Function_Helper: find_closest_color takes a calibrated_color translator, R,G, and B values and using euclidean shortest distance returns the most similar color
Expects: calibrated_colors be correctly calibrated as well as r, g, and b be within the range for a RGB value
Does: Returns the closest color to a given color using calibrated_colors 

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
These are used as helpers to remove the grid found on gifs downloaded from the various sources
Still in beta (working script needs better integration (handling file names through the process)

"""
"""
Function_Helper: get_most_common_color - Is used to get the most common color in a grid of 20 by 20 useful for removing a grid imposed on some gifs/images
Expects: Image be correctly initialized, grid_x, and grid_y be valid indexes of the 16 by 16 image
Does: Returns the most common color in a grid of 20 by 20 given the image 

"""
# Gets the most common color of the 16 by 16 (grids) image thats been scaled to 320 by 320
def get_most_common_color(image, grid_x, grid_y):
    # Get the dimensions of the image
    width, height = image.size

    # Calculate the grid boundaries
    left = grid_x * 20
    upper = grid_y * 20
    right = min((grid_x + 1) * 20, width)
    lower = min((grid_y + 1) * 20, height)

    # Crop the image to the grid boundaries
    grid_image = image.crop((left, upper, right, lower))

    # Get the colors of all pixels in the grid
    colors = grid_image.getcolors(grid_image.size[0] * grid_image.size[1])

    if colors is None:
        return (0, 0, 0)  # Return default color if no colors found in the grid

    # Find the most common color in the grid
    most_common_color = max(colors, key=lambda item: item[0])[1]

    return most_common_color

# Removes the grid imposed on the frames of the given gif
"""
Function: remove_grid_from_gif - Takes a gifs path and then iterates through each frame removing the grid from the frame and saving it to the gifs
Expects: gif_path point to a gif file 
Does: Removes the grid imposed on a 16 by 16 orignal resolution gif
"""
def remove_grid_from_gif(gif_path):
    print("Processing:", gif_path)
    # Open the GIF
    gif = Image.open(gif_path)

    # Create a list to store the modified frames
    modified_frames = []

    # Copy the frame rate (duration) of each frame from the original GIF
    durations = []

    # Skip the first frame when iterating over frames
    frames_iterator = ImageSequence.Iterator(gif)

    # Iterate over each frame
    for frame in frames_iterator:

        frame = frame.convert('RGB')
        # Create a new image to store the modified frame
        modified_frame = Image.new("RGB", frame.size, (0, 0, 0))  # Create a new image with a black background

        # Iterate over each grid in the frame
        for y in range(frame.height // 20):
            for x in range(frame.width // 20):
                # Get the most common color in the grid
                most_common_color = get_most_common_color(frame, x, y)

                # Replace all colors in the grid with the most common color
                for i in range(20):
                    for j in range(20):
                        modified_frame.putpixel((x * 20 + i, y * 20 + j), most_common_color)


        # Append the modified frame to the list of modified frames
        modified_frames.append(modified_frame)

        # Copy the duration of the frame from the original GIF
        durations.append(frame.info.get("duration", 100))

    # Save the modified frames as a new GIF
    modified_frames[0].save(
        gif_path,
        save_all=True,
        append_images=modified_frames[1:],
        loop=0,
        duration=durations
    )


"""
image path/ image to matrix

Assumptions - assumes that if square_side_length is the same as square_matrix_size then it should check to resize the image
    if it's not then it doesn't resize
"""
"""
Function: load_image_to_array - Takes a image, color, calibrated_colors, and the matrixes sides length and loads the image into a matrix
Expects: image_path_or_frame, color, calibrated, colors, and square_side_length be correctly initialized 
Does: Loads a image into a matrix of size square_side_length * square_side_length and returns it

"""
# take an image's path and convert it to a array of RGB values (or take it's shape as one color)
def load_image_to_array(image_path_or_frame, color, calibrated_colors, square_side_length):
    """Load an image and convert it to a two-dimensional array of RGB values."""

    red_boost = True

    if not isinstance(image_path_or_frame, Image.Image):
        # Open the image
        image = Image.open(image_path_or_frame)
        # Convert the image to RGB mode (in case it's not already in RGB)
        image = image.convert("RGB")
    else:
        # Convert the image to RGB mode (in case it's not already in RGB)
        image = image_path_or_frame.convert("RGB")

    # Get the dimensions of the image
    local_width, local_height = image.size

    # if their the same we assume we're ment to resize to the square_matrix_size (used for clock digits)
    if square_side_length == square_matrix_size:

        if local_height != square_matrix_size:
            image = image.resize((square_matrix_size, square_matrix_size), Image.NEAREST)

            # Get the dimensions of the image
            local_width, local_height = image.size


    # Create a two-dimensional array to store the RGB values
    image_array = [[(0, 0, 0) for _ in range(local_width)] for _ in range(local_height)]

    # Iterate over each pixel and store its RGB values in the array
    for y in range(local_height):
        for x in range(local_width):
            r, g, b = image.getpixel((x, y))

            if red_boost:
                if r > 5:
                    r += 20

                if b > 5:
                    b += 30
                g -= 5

                if r > 255:
                    r = 255

                if b > 255:
                    b = 255

                if g < 0:
                    g = 0

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
rotate_matrix is used for ease of use while rather inefficient it quickly allows a user to rotate their display
to improve ergonomics, functionality, and ease of use
"""
"""
Function_Helper: rotate_matrix - Takes a matrix and the rotate_k and rotates it by 90 degrees rotate_k times using numpy
Expects: the matrix be a square
Does: returns a k times 90 degrees rotated_matrix of the orignally passed matrix

"""
def rotate_matrix(matrix, rotate_k):
    # Convert the matrix to a NumPy array
    np_matrix = np.array(matrix)
    # Rotate the array clockwise by 90 degrees
    rotated_matrix = np.rot90(np_matrix, k=rotate_k)
    # Convert the rotated array back to a Python list
    rotated_matrix = rotated_matrix.tolist()
    return rotated_matrix


"""
OUNP - only update necessary pixels
In short this is the easiest quickest way to drastically (varies a lot on content) reduce both file sizes
but also the amount of pixels to change per frame. Meaning either much larger matrixes can be updated at the same FPS
or much higher FPS can be achieved.

Potential to improve. Look for ways to remove even more unnecessary updates by looking for small changes in color (imperceptible)
"""
"""
Function: only_update_necessary_pixels - This function takes the previous frame (in a series of frames) and the current frame and returns
a matrix containing boolean values indicating if the pixel in each corresponding index has changed (indicating we need to update information)
Expects: previous_image_array, and current_image_array are matrixes same size matrixes and matrixes holding color information
Does: Returns a boolean matrix indicating which indexes colors changed from the previous and current frames

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
takes the previous frame, current frame, and the .ani file name and writes the current frame to the file 

"""
"""
Function: print_frame_to_file - Take a file_name, previous_image_array, and current_image_array indicates what pixels are 
changed and writes it to a .ani file in .ani file format
Expects: file_name, previous_image_array, and current_image_array are initialized and containing valid information 
(path exists and matrixes contain color information and are same size) 
Does: Prints the changes between the frames in .ani format

"""
# takes the image_array (array of a images RGB values) and prints it to the .ani file
def print_frame_to_file(file_name, previous_image_array, current_image_array):
    height = len(current_image_array)
    width = len(current_image_array[0])

    # if the user wants the final result to be rotated then rotate it
    if rotate_k != 0:
        previous_image_array = rotate_matrix(previous_image_array, rotate_k)
        current_image_array = rotate_matrix(current_image_array, rotate_k)


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
        file.flush()


"""
EFFECTS
"""

"""
falling astroids helpers
"""
"""
Function_Helper: probability_check generates a random number within the given numerator and denominator and returns 
if the random number is less than the numerator. AKA coinflip with probability indicated by numerator and denominator
Expects: numerator, and denominator are intiailized and importantly dictate a valid probability
Does: Returns a coinflip with probability indicated by the numerator and denomiator

"""
def probability_check(numerator, denominator):
    # Generate a random number between 0 and denominator - 1
    random_number = random.randint(0, denominator - 1)
    # Check if the random number falls within the probability range
    return random_number < numerator

"""
Function_Helper: sift_down - simply takes a matrix and shifts each matrixes index down (REMOVING TOP ROW)
Expects: matrix be intiailzied and contain color information
Does: Returns the given matrix of colors with each index shifted down in Y axis

"""
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
"""
Function: failing_astroids_effect - takes the time, framerate, filename, matrix side length, and calibration dictionary 
and makes length_of_time * frame_rate number of frames of the falling_astroids_effect saving them to the given .ani file_name
Expects: length_of_time, frame_rate, file_name, square_matrix,size, and calibration file all correctly intiialized
Does: Makes a .ani file containing frame data demonstrating the falling_astroids_effect

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

                r, g, b = pick_random_color()

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
"""
Function: bouncing_ball - given length_of_time, frame_rate, file_name, and square_matrix_size and makes frames 
showcasing a bouncing ball saving them to the .ani file_name
Expects: length_of_time, frame_rate, file_name, square_matrix_size all correctly initialized
Does: Prints frames to the given file_name .ani showcasing a ball bouncing around

"""
def bouncing_ball(length_of_time, frame_rate, file_name, square_matrix_size, calibration_dictionary):
    direction_dictionary = {'down': (1, 0), 'up': (-1, 0), 'right': (0, 1), 'left': (0, -1), 'down_right': (1, 1),
                            'down_left': (1, -1), 'up_right': (-1, 1), 'up_left': (-1, -1)}

    num_balls = int(input("Please enter the number of balls: "))

    balls = []

    for _ in range(num_balls):
        r, g, b = pick_random_color()
        while r == 0 and g == 0 and b == 0:
            r, g, b = pick_random_color()
        new_ball = {
            'col_of_ball': random.randint(0, square_matrix_size - 1),
            'row_of_ball': random.randint(0, square_matrix_size - 1),
            'col_direction': 1,
            'row_direction': 1,
            'hit_wall_flag': False,
            'r_g_b': (r, g, b),
            'randomness_modifier': random.randint(1, 4)
        }
        balls.append(new_ball)

    frame_count = 0
    image_array = [[(0, 0, 0) for _ in range(square_matrix_size)] for _ in range(square_matrix_size)]
    previous_image_array = [[(0, 0, 0) for _ in range(square_matrix_size)] for _ in range(square_matrix_size)]

    while frame_count < (frame_rate * length_of_time):
        previous_image_array = [row[:] for row in image_array]  # Create a deep copy of image_array
        for ball in balls:
            try:


                col_of_ball = ball['col_of_ball']
                row_of_ball = ball['row_of_ball']
                col_direction = ball['col_direction']
                row_direction = ball['row_direction']
                hit_wall_flag = ball['hit_wall_flag']
                r, g, b = ball['r_g_b']
                randomness_modifier = ball['randomness_modifier']

                # Clear the previous position of the ball
                image_array[col_of_ball][row_of_ball] = (0, 0, 0)

                # Check if the next position will be out of bounds
                next_col = col_of_ball + col_direction
                next_row = row_of_ball + row_direction

                # Randomly change direction if needed
                if hit_wall_flag:
                    randomness_modifier = random.randint(1, 4)
                    hit_wall_flag = False

                if next_col < 0 or next_col >= square_matrix_size:
                    coin_flip = random.randint(1, 100)
                    if coin_flip > 95:
                        r, g, b = pick_random_color()
                        while r == 0 and g == 0 and b == 0:
                            r, g, b = pick_random_color()
                    hit_wall_flag = True
                    col_direction *= -1  # Change the direction
                    col_of_ball += col_direction  # Adjust the position
                else:
                    col_of_ball = next_col  # Update the column position

                if next_row < 0 or next_row >= square_matrix_size:
                    coin_flip = random.randint(1, 100)
                    if coin_flip > 95:
                        r, g, b = pick_random_color()
                        while r == 0 and g == 0 and b == 0:
                            r, g, b = pick_random_color()

                    hit_wall_flag = True
                    row_direction *= -1  # Change the direction
                    row_of_ball += row_direction  # Adjust the position
                else:
                    row_of_ball = next_row  # Update the row position

                coin_flip = random.randint(1, 100)
                if coin_flip > 92:
                    coin_flip = random.randint(1, 2)
                    if randomness_modifier == 1:
                        if coin_flip == 1:
                            if (col_of_ball + 1) <= square_matrix_size - 1:
                                col_of_ball = col_of_ball + 1
                        else:
                            if (col_of_ball - 1) >= 0:
                                col_of_ball = col_of_ball - 1
                    else:
                        if coin_flip == 1:
                            if (row_of_ball + 1) <= square_matrix_size - 1:
                                row_of_ball = row_of_ball + 1
                        else:
                            if (row_of_ball - 1) >= 0:
                                row_of_ball = row_of_ball - 1

                # Update the ball's position in the image_array
                image_array[col_of_ball][row_of_ball] = (r, g, b)

                ball['col_of_ball'] = col_of_ball
                ball['row_of_ball'] = row_of_ball
                ball['col_direction'] = col_direction
                ball['row_direction'] = row_direction
                ball['hit_wall_flag'] = hit_wall_flag
                ball['r_g_b'] = (r, g, b)
                ball['randomness_modifier'] = randomness_modifier

            except IndexError:
                hit_wall_flag = True  # Set flag if the ball hits the wall

        # Print the frame to the file
        print_frame_to_file(file_name, previous_image_array, image_array)
        frame_count += 1


"""
Moving lines helper function
"""
"""
Function_Helper: array_to_matrix - takes the image_array, and converts it to a matrix
Expects: image_array, rows, and cols all are initialized
Does: returns the image_array as a matrix

"""
def array_to_matrix(image_array, rows, cols):
    matrix = []
    for i in range(0, len(image_array), cols):
        matrix.append(image_array[i:i+cols])
    return matrix

"""
Moving lines function
"""
"""
Function: moving_lines - takes length_of_time, frame_rate, file_name, and square_matrix_size and creates frames 
showcasing colors lines moving across the panel printing these frames to the indicated .ani file
Expects: length_of_time, frame_rate, file_name, square_matrix_size are all correctly initialized
Does: Prints frames containing color lines moving around the panel to the indicated .ani file_name

"""
def moving_lines(length_of_time, frame_rate, file_name, square_matrix_size, calibration_dictionary):
    length_of_line = input("Please enter the number of pixels each line should be: ")
    length_of_line = int(length_of_line)

    image_as_one_dimensional_array = [(0, 0, 0)] * (square_matrix_size * square_matrix_size)

    # Create the blanked out image_array filled with black pixels
    image_array = [[(0, 0, 0) for _ in range(square_matrix_size)] for _ in range(square_matrix_size)]
    # Create the blanked out image_array filled with black pixels
    previous_image_array = [[(0, 0, 0) for _ in range(square_matrix_size)] for _ in range(square_matrix_size)]

    frame_count = 0

    while frame_count < (length_of_time * frame_rate):

        r, g, b = pick_random_color()
        while r == 0 and g == 0 and b == 0:
            r, g, b = pick_random_color()

        for i in range(0, length_of_line):
            image_as_one_dimensional_array[0] = r, g, b
            #print(image_as_one_dimensional_array)
            previous_image_array = [row[:] for row in image_array]  # Create a deep copy of image_array
            image_array = array_to_matrix(image_as_one_dimensional_array, square_matrix_size, square_matrix_size)
            #print(image_array)
            print_frame_to_file(file_name, previous_image_array, image_array)
            frame_count = frame_count + 1

            for j in range(len(image_as_one_dimensional_array) - 1, 0, -1):
                image_as_one_dimensional_array[j] = tuple(image_as_one_dimensional_array[j - 1])


"""
End effects
"""


"""
GIF helper
"""
"""
Function_Helper: get_gif_fps returns the fps of the given gif file_name
Expects: file_path point to a valid gif file
Does: returns the fps of the indicated gif file_name

"""
# gets the gif's FPS
def get_gif_fps(file_path):
    with Image.open(file_path) as img:
        duration = img.info['duration']  # Get the duration of each frame in milliseconds
        fps = 1000 / duration  # Convert duration from milliseconds to seconds
        return fps

"""
Function_Helper: get_gif_number_of_frames returns how many frames are in the gif file_name
Expects: file_name points to a valid gif file
Does: returns the number of frames in the gif

"""
# gets the number of frames in a gif
def get_gif_number_of_frames(file_path):
    with Image.open(file_path) as img:
        total_frames = img.n_frames  # Get the total number of frames
        return total_frames



"""
Clock methods

"""
# takes the image_array (array of a images RGB values) and prints it to the .ani file
"""
Function_debug: print_frame_to_file_debug performs the same operation as print_frame_to_file except doesn't perform
OUNP for debugging reasons
Expects: same as print_frame_to_file
Does: same as print_frame_to_file

"""
def print_frame_to_file_debug(file_name, previous_image_array, current_image_array):
    height = len(current_image_array)
    width = len(current_image_array[0])
    
    if rotate_k != 0:
        
        previous_image_array = rotate_matrix(previous_image_array, rotate_k)
        current_image_array = rotate_matrix(current_image_array, rotate_k)
    
    # get what pixels to update from OUNP
    pixels_to_update  = only_update_necessary_pixels(previous_image_array, current_image_array)
    
    with open(file_name + ".ani", "a") as file:
        file.write(" ")
        for x in range(width):  # Iterate over columns
            if x % 2 == 0:  # Even columns
                for y in range(height):  # Iterate over rows in each column
                    count = x * height + y
                    r1, g1, b1 = current_image_array[y][x]  # Access pixel at (x, y)
                    file.write(f"{count} {r1} {g1} {b1}, ")

            else:  # Odd columns
                for y in range(height - 1, -1, -1):  # Iterate over rows in reverse order
                    count = x * height + (height - 1 - y)
                    r1, g1, b1 = current_image_array[y][x]  # Access pixel at (x, y)
                    file.write(f"{count} {r1} {g1} {b1}, ")
        file.write("\n")

"""
Function_Helper: imprint_matrix - takes a image_array and imprints the given character onto the image_array
Expects: image_array, row, col, character, font_color, and calibration dictionary are all intialized
Does: Returns the image_array except with the indicated character imprinting onto the array in the position specifiied by row and col

"""
def imprint_matrix(row, col, image_array, character, font_color, calibration_dictionary):
    character_array = []

    if character == ':':
        character_array = load_image_to_array("Digits/" + str("colon") + ".png", font_color, calibration_dictionary, -1)
    else:
        character_array = load_image_to_array("Digits/" + str(character) + ".png", font_color, calibration_dictionary, -1)



    character_array = np.array(character_array)
    image_array = np.array(image_array)


    # Starting row and column index in the target array
    start_row = row
    start_col = col

    # Get the dimensions of the source and target arrays
    source_rows = len(character_array)
    source_cols = len(character_array[0])
    target_rows = len(image_array)
    target_cols = len(image_array[0])

    # Calculate the ending row and column index in the target array
    end_row = min(start_row + source_rows, target_rows)
    end_col = min(start_col + source_cols, target_cols)

    # Place the source array into the target array
    image_array[start_row:end_row, start_col:end_col] = character_array[:end_row - start_row, :end_col - start_col]

    image_array = image_array.tolist()
    return image_array

"""
Function: clock_generator - takes a file_name, font_color, row_offset, col_offset and generates the .ani for 
a clock from midnight to midnight
Expects: file_name, font_color, row_offset, col_offset are all valid and initialized
Does: generates frames of each minute of a clock from midnight to midnight and prints the frame data to a .ani file_name

"""
def clock_generator(file_name, font_color, row_offset, col_offset, calbration_dictionary):

    digit_col_length = 3
    colon_length = 2

    # Create the blanked out image_array filled with black pixels
    previous_image_array = [[(0, 0, 0) for _ in range(square_matrix_size)] for _ in range(square_matrix_size)]
    # Create the blanked out image_array filled with black pixels
    current_image_array = [[(0, 0, 0) for _ in range(square_matrix_size)] for _ in range(square_matrix_size)]
    
    for k in range(0,2):
        for j in range(0, 60):
            i = 12
            first_digit = i // 10
            if int(first_digit) == 1:
                current_image_array = imprint_matrix(row_offset, col_offset, current_image_array, first_digit, font_color, calibration_dictionary)
                second_digit = i % 10
                current_image_array = imprint_matrix(row_offset, col_offset + (digit_col_length * 1) + 1, current_image_array, second_digit, font_color, calibration_dictionary)
            else:
                second_digit = i % 10
                current_image_array = imprint_matrix(row_offset, col_offset + (digit_col_length * 1) + 1, current_image_array, second_digit, font_color, calibration_dictionary)


            current_image_array = imprint_matrix(row_offset + 1, col_offset + (digit_col_length * 2) + 1, current_image_array, ':', font_color, calibration_dictionary)

            third_digit = j // 10
            current_image_array = imprint_matrix(row_offset, col_offset + (digit_col_length * 2) + 1 + colon_length, current_image_array, third_digit, font_color, calibration_dictionary)
            fourth_digit = j % 10
            current_image_array = imprint_matrix(row_offset, col_offset + (digit_col_length * 3) + 2 + colon_length, current_image_array, fourth_digit, font_color, calibration_dictionary)



            print_frame_to_file_debug(file_name, previous_image_array, current_image_array)
            previous_image_array = current_image_array
            current_image_array = [[(0, 0, 0) for _ in range(width)] for _ in range(height)]

        for i in range(1, 12):
            for j in range(0, 60):
                first_digit = i // 10
                if int(first_digit) == 1:
                    current_image_array = imprint_matrix(row_offset, col_offset, current_image_array, first_digit, font_color, calibration_dictionary)
                    second_digit = i % 10
                    current_image_array = imprint_matrix(row_offset, col_offset + (digit_col_length * 1) + 1, current_image_array, second_digit, font_color, calibration_dictionary)
                else:
                    second_digit = i % 10
                    current_image_array = imprint_matrix(row_offset, col_offset + (digit_col_length * 1) + 1, current_image_array, second_digit, font_color, calibration_dictionary)


                current_image_array = imprint_matrix(row_offset + 1, col_offset + (digit_col_length * 2) + 1, current_image_array, ':', font_color, calibration_dictionary)

                third_digit = j // 10
                current_image_array = imprint_matrix(row_offset, col_offset + (digit_col_length * 2)  + 1 + colon_length, current_image_array, third_digit, font_color, calibration_dictionary)
                fourth_digit = j % 10
                current_image_array = imprint_matrix(row_offset, col_offset + (digit_col_length * 3) + 2 + colon_length, current_image_array, fourth_digit, font_color, calibration_dictionary)

                print_frame_to_file_debug(file_name, previous_image_array, current_image_array)
                previous_image_array = current_image_array
                current_image_array = [[(0, 0, 0) for _ in range(width)] for _ in range(height)]



"""
Calibration File Reader - NOTE CURRENTLY UNUSED AS COLOR quality was significantly better than expected but code is functional
"""
# Function to read calibration data from a file and store it in a dictionary
"""
DEPRECATED to be removed
"""
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
    calibration_dictionary = read_calibration_file("calibration.cal")

else:
    calibration_dictionary = None

# DONT USE CALIBRATION FILE SINCE COLORS ARE SATISFACTORY
calibration_dictionary = None

# Ask the user if they want the final frame to be rotated
#rotate_k = int(input("Please input K value: "))

# driver code that determines what type of animation the user wants and then walks them through the selections and creates the .ani file
option = input("Please enter \n1 folders of images\n2 text \n3 gif \n4 video"
                + "\n5 Effects \n6 24 hour clock\n7 itinerary\n8 single images\n:")

# Create the blanked out image_array filled with black pixels
image_array = [[(0, 0, 0) for _ in range(width)] for _ in range(height)]

# images
if int(option) == 1:
    # Prompt the user for input
    folders_name = input("Please enter the folder's name: ") + "/"

    numbered_or_random = input("Are the images numbered 1-x?(Y/N):")

    if numbered_or_random.lower() == "y":

        number_of_pictures = int(input("Please enter the number of frames: "))
        file_name = input("Please enter the name for the output file: ")
        frame_rate = input("Please enter the desired frames per second: ")

        # Prepare the file path
        file_path = file_name + ".ani"

        calibration_dictionary = None

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
            image_array = load_image_to_array(folders_name + str(i) + ".png", None, calibration_dictionary, square_matrix_size)
            print_frame_to_file(file_name, previous_image_array, image_array)

    else:
        number_of_pictures = os.listdir(folders_name)
        file_name = input("Please enter the name for the output file: ")
        frame_rate = input("Please enter the desired frames per second: ")

        # Prepare the file path
        file_path = file_name + ".ani"

        calibration_dictionary = None

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

        # Iterate over each file in the folder
        for current_file in os.listdir(folders_name):
            previous_image_array = image_array
            image_array = load_image_to_array(folders_name + "/" + current_file, None, calibration_dictionary,
                                              square_matrix_size)
            print_frame_to_file(file_name, previous_image_array, image_array)


# Text
elif int(option) == 2:
    # Prompt the user for text input
    text = input("Please enter the text you want: ")
    font_color = input("Please enter a color from the list. Options are:\nred, green, blue,\nblack, white, yellow,\ncyan, magenta, purple,\norange, pink, brown,\ngray, light_gray, dark_gray,\nolive, teal, navy: ")
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

    calibration_dictionary = None

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
            image_array = load_image_to_array("Alphabet/" + str(i) + ".png", font_color, calibration_dictionary, square_matrix_size)
            print_frame_to_file(file_name, previous_image_array, image_array)
        elif i.islower():
            image_array = load_image_to_array("Alphabet/" + str(i) + "l" + ".png", font_color, calibration_dictionary, square_matrix_size)
            print_frame_to_file(file_name, previous_image_array, image_array)
        elif i.isspace():
            image_array = load_image_to_array("Alphabet/" + "space" + ".png", font_color, calibration_dictionary, square_matrix_size)
            print_frame_to_file(file_name, previous_image_array, image_array)

# GIF
elif int(option) == 3:

    folder_or_file = input("Would you like to convert a folder of gifs?(Y/N)")

    if folder_or_file.lower() == "n":

        # Prompt the user for GIF input
        gif_name = input("Please enter the file name of the gif: ")
        gif_name = gif_name.replace('"', '').replace("'", "")
        file_name = input("Please enter the output files name: ")
        custom_fps = input("Do you want a custom FPS?(Y/N): ")
        insert_black_frame = input("Insert a black frame at end of gif? (Y/N): ")
        remove_grid = input("Remove a grid? (Y/N): ")

        gif_type_check = gif_name[-4:]

        if gif_type_check.lower() != '.gif':
            gif_name = gif_name + ".gif"

        if remove_grid.lower() == 'y':
            remove_grid_from_gif(gif_name)
            #gif_name = "grid_removal/modified.gif"

        if custom_fps.lower() == 'n':
            # Get the frames per second from the GIF
            fps = get_gif_fps(gif_name)
        else:
            fps = int(input("Please enter the desired FPS: "))

        # Prepare the file path
        file_path = file_name + ".ani"

        calibration_dictionary = None

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
            file.write("Length: " + str(get_gif_number_of_frames(gif_name)) + "\n")
            file.write("Type: gif\n")
            file.write("Side_Length: " + str(square_matrix_size) + "\n")

        gif = Image.open(gif_name)
        # Iterate over each frame in the GIF and add it to the animation file
        while True:
            try:
                gif.seek(gif.tell() + 1)
            except EOFError:
                break

            frame = gif.copy().resize((square_matrix_size, square_matrix_size), Image.NEAREST)

            previous_image_array = image_array
            image_array = load_image_to_array(frame, None, calibration_dictionary, square_matrix_size)

            print_frame_to_file_debug(file_name, previous_image_array, image_array)

        if insert_black_frame.lower() == 'y':
            image_array = [[(0, 0, 0) for _ in range(square_matrix_size)] for _ in range(square_matrix_size)]
            print_frame_to_file_debug(file_name, previous_image_array, image_array)

    else:
        # Prompt the user to input a folder containing GIF files
        folder_path = input("Enter the folder path containing GIF files: ")
        folder_path = folder_path.replace('"', '').replace("'", "")
        remove_grid = input("Remove a grid? (Y/N): ")

        # Iterate over each file in the folder
        for filename in os.listdir(folder_path):
            # Create the blanked out image_array filled with black pixels
            previous_image_array = [[(0, 0, 0) for _ in range(square_matrix_size)] for _ in range(square_matrix_size)]
            # Create the blanked out image_array filled with black pixels
            image_array = [[(0, 0, 0) for _ in range(square_matrix_size)] for _ in range(square_matrix_size)]
            if filename.endswith(".gif") or filename.endswith(".GIF"):
                gif_path = os.path.join(folder_path, filename)

                if remove_grid.lower() == 'y':
                    remove_grid_from_gif(gif_path)

                # Get the frames per second from the GIF
                fps = get_gif_fps(gif_path)

                file_name = filename[:-4]

                # Prepare the file path
                file_path = folder_path + "/" + file_name + ".ani"

                calibration_dictionary = None

                # Remove the file if it already exists
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print("File deleted successfully.")
                else:
                    print("File does not exist.")

                # Write animation metadata to the file
                with open(file_path, "a") as file:
                    file.write("\"\n")
                    file.write("\"\n")
                    file.write("FPS: " + str(fps) + "\n")
                    file.write("Length: " + str(get_gif_number_of_frames(gif_path)) + "\n")
                    file.write("Type: gif\n")
                    file.write("Side_Length: " + str(square_matrix_size) + "\n")

                if not os.path.exists(gif_path):
                    print("error invalid paths")
                    sys.exit(1) # type: ignore
                gif = Image.open(gif_path)

                file_path = file_path[:-4]

                # Iterate over each frame in the GIF and add it to the animation file
                while True:
                    try:
                        gif.seek(gif.tell() + 1)
                    except EOFError:
                        break

                    frame = gif.copy().resize((square_matrix_size, square_matrix_size), Image.NEAREST)

                    previous_image_array = image_array
                    image_array = load_image_to_array(frame, None, calibration_dictionary, square_matrix_size)

                    print_frame_to_file_debug(file_path, previous_image_array, image_array)



# Placeholder for video
elif int(option) == 4:
    print("This feature isn't currently implemented")

# Effects
elif int(option) == 5:
    # Prompt the user for effect input
    effect_option = int(input("Select an effect \n1 falling asteroids\n2 bouncing ball\n3 moving lines\n:"))
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
    elif effect_option == 3:
        moving_lines(length_of_time, frame_rate, file_name, square_matrix_size, calibration_dictionary)

# Clock
elif int(option) == 6:
    if square_matrix_size <= 8:
        print("clock isn't able to be shown on such a small display\n")
        exit()
    else:
        file_name = input("Please enter the output file name: ")
        font_color = input("Please enter a color from the list. Options are:\nred, green, blue,\nwhite, yellow,\ncyan, magenta, purple,\norange, pink, brown,\ngray, light_gray, dark_gray,\nolive, teal, navy: ")
        should_center = input("Want it column centered? (Y/N): ")
        if should_center.lower() == 'y':
            if square_matrix_size > 16:
                col_offset = (((square_matrix_size // 16) // 2) * 16) - 8
                row_offset = 0
            else:
                col_offset = 0
                row_offset = 0
        else:
            should_manual_offset = input("Want to give manual row/column offsets? (Y/N): ")
            if should_manual_offset.lower() == 'y':
                row_offset = input("Please enter the row offset desired: ")
                col_offset = input("Please enter the column offset desired: ")
            else:
                row_offset = 0
                col_offset = 0


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
            #TODO unblock
            #file.write("FPS: " + str("0.016666666667") + "\n")
            file.write("FPS: " + str("24") + "\n")
            file.write("Length: " + str("1440") + "\n")
            file.write("Type: clock\n")
            file.write("Side_Length: " + str(square_matrix_size) + "\n")

        clock_generator(file_name, font_color, int(row_offset), int(col_offset), calibration_dictionary)

elif int(option) == 7:
    seconds_to_account_for = 86400

    print("Welcome to the itinerary maker. Essentially a whole day is cut up into just seconds.\nSo you will be asked what file you want and then how long it should play.\nThis continues until all 86400 seconds are used.\n")
    itinerary_file_name = input("Please enter the name of the itinerary file (without .iti extentsion): ")
    random_gifs = input(("Want to just show random gifs? (Y/N): "))

    if random_gifs.lower() == "n":

        while seconds_to_account_for > 0:
            file_name = input("Please enter the files name or path (with name): ")

            extentsion_check = file_name[-4:]

            if extentsion_check.lower() != ".ani":
                file_name = file_name + ".ani"

            seconds_played = int(input("Please enter how many seconds it should play for: "))
            while seconds_to_account_for - seconds_played < 0:
                seconds_played = int(input("Thats too long you only have " + str(seconds_to_account_for) + " to allot for enter a new number: "))


            with open(itinerary_file_name + '.iti', 'a') as file:
                file.write((str(seconds_to_account_for) + " - " + str(seconds_to_account_for - seconds_played) + " : " + str(file_name) + "\n"))

            seconds_to_account_for = seconds_to_account_for - seconds_played

    else:
        gifs = []
        # Remove the file if it already exists
        if os.path.exists(itinerary_file_name + ".iti"):
            os.remove(itinerary_file_name + ".iti")
            print("File deleted successfully.")
        else:
            print("File does not exist.")

        # Iterate over each file in the folder
        for filename in os.listdir("random_gif_anis"):
            if filename.endswith(".ANI") or filename.endswith(".ani"):
                gif_path = os.path.join("random_gif_anis", filename)
                # Perform grid removal on the GIF and replace it with the modified version
                with open(gif_path, "r") as file:
                    line = file.readline()
                    while True:
                        line = file.readline()
                        if "\"" in line:
                            line = file.readline()
                            break
                    fps = line.split().pop()
                    length = file.readline()
                    length = length.split().pop()


                gifs.append((gif_path, int(round(int(float(length))//int(float(fps))))))

        while seconds_to_account_for > 0:
            gif_path, duration = random.choice(gifs)

            seconds_played = random.randint(2, 5) * duration

            with open(itinerary_file_name + '.iti', 'a') as file:
                file.write((str(seconds_to_account_for) + " - " + str(seconds_to_account_for - seconds_played) + " : " + str(gif_path) + "\n"))

            seconds_to_account_for = seconds_to_account_for - seconds_played

# single image
elif int(option) == 8:
    # Prompt the user for input
    pictures_path = input("Please enter the pictures path: ") + "/"

    file_name = input("Please enter the name for the output file: ")

    # Prepare the file path
    file_path = file_name + ".ani"

    calibration_dictionary = None

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
        file.write("FPS: 1" + "\n")
        file.write("Length: 1" + "\n")
        file.write("Type: image\n")
        file.write("Side_Length: " + str(square_matrix_size) + "\n")


    previous_image_array = image_array

    image_array = load_image_to_array(pictures_path, None, calibration_dictionary,
                                          square_matrix_size)
    print_frame_to_file(file_name, previous_image_array, image_array)
