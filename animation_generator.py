"""
Austin Lunbeck
animation_generator.py

this is a simple python script that creates a .ani file for my LED panel. 
.ani file type supports
full RGB range, comments, FPS, type distinction, and only necesary pixel updating (ONPU) coming soon after refactor

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

square_matrix_size = 8

# Define the dimensions of the image_array
width = square_matrix_size
height = square_matrix_size


"""
variable that holds last frame that was printed (for optimization)
"""
# Create the blanked out image_array filled with black pixels
old_image_array = [[(0, 0, 0) for _ in range(width)] for _ in range(height)]


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
image path/ image to matrix
"""
# take an image's path and convert it to a array of RGB values (or take it's shape as one color) 
def load_image_to_array(image_path_or_frame, color):
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
    
    # Create a two-dimensional array to store the RGB values
    image_array = [[None] * width for _ in range(height)]
    
    # Iterate over each pixel and store its RGB values in the array
    for y in range(height):
        for x in range(width):
            r, g, b = image.getpixel((x, y))
            if color is None:
                image_array[y][x] = (r, g, b)
            else:
                if r != 0 or g != 0 or b != 0:
                    r, g, b = get_color_rgb_load(color)
                    image_array[y][x] = (r, g, b)
                else:
                    r, g, b = get_color_rgb_load("black")
                    image_array[y][x] = (r, g, b)
    
    return image_array


"""
Image_array/.ani printer

"""
# takes the image_array (array of a images RGB values) and prints it to the .ani file
def print_frame_to_file(file_name, current_image_array):
    height = len(current_image_array)
    width = len(current_image_array[0])
    with open(file_name + ".ani", "a") as file:
        file.write(" ")
        for x in range(width):  # Iterate over columns
            if x % 2 == 0:  # Even columns
                for y in range(height):  # Iterate over rows in each column
                    r1, g1, b1 = current_image_array[y][x]  # Access pixel at (x, y)
                    count = x * height + y
                    file.write(f"{count} {r1} {g1} {b1}, ")
                        
            else:  # Odd columns
                for y in range(height - 1, -1, -1):  # Iterate over rows in reverse order
                    r1, g1, b1 = current_image_array[y][x]  # Access pixel at (x, y)
                    count = x * height + (height - 1 - y)
                    file.write(f"{count} {r1} {g1} {b1}, ")
        file.write("\n")



"""
falling astroids helpers
"""
def probability_check(numerator, denominator):
    # Generate a random number between 0 and denominator - 1
    random_number = random.randint(0, denominator - 1)
    # Check if the random number falls within the probability range
    return random_number < numerator

def shift_down(matrix):
    """
    Shifts each index in a matrix down by one in the x direction.

    Args:
        matrix (list of lists): The input matrix.

    Returns:
        list of lists: The shifted matrix.
    """
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

def falling_astroids_effect(length_of_time, frame_rate, file_name, probability, square_matrix_size):
    number_of_frames_to_generate = length_of_time * frame_rate
    frame_count = 0
    # Create the blanked out image_array filled with black pixels
    image_array = [[(0, 0, 0) for _ in range(square_matrix_size)] for _ in range(square_matrix_size)]
    create_new_astroid = False
    non_taken_positions = list(range(square_matrix_size))  # Initialize non_taken_positions

    while frame_count < number_of_frames_to_generate:

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
                image_array[0][position] = (r, g, b)
                non_taken_positions.remove(position)
            else:  # If all positions are taken, reset non_taken_positions
                non_taken_positions = list(range(square_matrix_size))

        print_frame_to_file(file_name, image_array)
        frame_count += 1



"""
GIF helper
"""
# gets the gif's FPS
def get_gif_fps(file_path):
    with Image.open(file_path) as img:
        duration = img.info['duration']  # Get the duration of each frame in milliseconds
        total_frames = img.n_frames  # Get the total number of frames
        fps = 1000 / duration  # Convert duration from milliseconds to seconds
        return fps
    
# gets the number of frames in a gif
def get_gif_number_of_frames(file_path):
    with Image.open(file_path) as img:
        total_frames = img.n_frames  # Get the total number of frames
        return total_frames



"""
DRIVER

"""
# driver code that determines what type of animation the user wants and then walks them through the selections and creates the .ani file
option = input("Please enter \n1 to convert a folders images to animations\n2 to convert text to animations \n3 to convert a gif \n4 to convert a video"
                + "\n5 Effects \n:")


# images
if int(option) == 1:
    
    folders_name = input("Please enter the folders name: ") + "/"
    number_of_pictures = input("Please enter the number of frames: ")
    file_name = input("Please enter the name for the output file: ")
    frame_rate = input("Please enter the desired frames per second: ")

    file_path = file_name + ".ani"

    if os.path.exists(file_path):
        os.remove(file_path)
        print("File deleted successfully.")
    else:
        print("File does not exist.")
        
    with open(file_name + ".ani", "a") as file:
        file.write("\"\n")
        file.write("\"\n")
        file.write("FPS: " + str(frame_rate) + "\n")
        file.write("Length: " + str(len(number_of_pictures)) + "\n")
        file.write("Type: images\n")

    for i in range(1, int(number_of_pictures) + 1):
        image_array = load_image_to_array(folders_name + str(i) + ".png", None)
        print_frame_to_file(file_name, image_array)
        old_image_array = image_array
        
# Text
elif int(option) == 2:
    text = input("Please enter the text you want: ")
    color = input("Please enter a color from the list. Options are:\nred, green, blue,\nblack, white, yellow,\ncyan, magenta, purple,\norange, pink, brown,\ngray, light_gray, dark_gray,\nolive, teal, navy: ")
    file_name = input("Please enter the name for the output file: ")
    frame_rate = input("Please enter the desired frames per second: ")
    
    file_path = file_name + ".ani"

    if os.path.exists(file_path):
        os.remove(file_path)
        print("File deleted successfully.")
    else:
        print("File does not exist.")
    
    with open(file_name + ".ani", "a") as file:
        file.write("\"\n")
        file.write("\"\n")
        file.write("FPS: " + str(frame_rate) + "\n")
        file.write("Length: " + str(len(text)) + "\n")
        file.write("Type: text\n")
        
    for i in text:
        if i.isupper():
            image_array = load_image_to_array("Alphabet/" + str(i) + ".png", color)
            print_frame_to_file(file_name, image_array)
            old_image_array = image_array
        elif i.islower():
            image_array = load_image_to_array("Alphabet/" + str(i) + "l" + ".png", color)
            print_frame_to_file(file_name, image_array)
            old_image_array = image_array
        elif i.isspace():
            image_array = load_image_to_array("Alphabet/" + "space" + ".png", color)
            print_frame_to_file(file_name, image_array)
            old_image_array = image_array

# GIF
elif int(option) == 3:
    gif_name = input("Please enter the file name of the gif: ")
    file_name = input("Please enter the output files name: ")
    
    fps = get_gif_fps(gif_name + ".gif")

    file_path = file_name + ".ani"

    if os.path.exists(file_path):
        os.remove(file_path)
        print("File deleted successfully.")
    else:
        print("File does not exist.")
        
    with open(file_name + ".ani", "a") as file:
        file.write("\"\n")
        file.write("\"\n")
        file.write("FPS: " + str(fps) + "\n")
        file.write("Length: " + str(get_gif_number_of_frames(gif_name + ".gif")) + "\n")
        file.write("Type: gif\n")
        
    gif = Image.open(gif_name + ".gif")    
    
    # Iterate over each frame
    while True:
        # Get the current frame
        try:
            gif.seek(gif.tell() + 1)
        except EOFError:
            break
    
        # Process the frame
        frame = gif.copy().resize((square_matrix_size, square_matrix_size))
        
        image_array = load_image_to_array(frame, None)
        
        print_frame_to_file(file_name, image_array)
        old_image_array = image_array

# Place holder for video
elif int(option) == 4:
    print("This feature isn't currently implemented")

# Effects
elif int(option) == 5:
    effect_option = int(input("Select an effect \n1 falling astroids\n: "))
    length_of_time = int(input("Length of time for the animation in seconds: "))
    frame_rate = int(input("Desired frame rate: "))
    probability = int(input("Please enter the probability of of 100: "))
    file_name = input("Please enter the output file name: ")

    file_path = file_name + ".ani"

    if os.path.exists(file_path):
        os.remove(file_path)
        print("File deleted successfully.")
    else:
        print("File does not exist.")
        
    with open(file_name + ".ani", "a") as file:
        file.write("\"\n")
        file.write("\"\n")
        file.write("FPS: " + str(frame_rate) + "\n")
        file.write("Length: " + str(int(frame_rate * length_of_time)) + "\n")
        file.write("Type: effect\n")

    falling_astroids_effect(length_of_time, frame_rate, file_name, probability, square_matrix_size)

