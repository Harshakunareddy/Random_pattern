import turtle
import os
import io
import cv2
from PIL import Image
import mysql.connector
import configparser

# Read configuration from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

db_params = {
    'host': config.get('MySQL', 'host'),
    'user': config.get('MySQL', 'user'),
    'password': config.get('MySQL', 'password'),
    'database': config.get('MySQL', 'database'),
}

image_folder = config.get('Paths', 'image_folder')
output_video = config.get('Paths', 'output_video')

line_shape = config.get('Turtle', 'line_shape')
line_thickness = config.getint('Turtle', 'line_thickness')

fps = config.getint('Video', 'fps')
video_resolution = tuple(map(int, config.get('Video', 'video_resolution').split('x')))

os.makedirs(image_folder, exist_ok=True)

# ... (rest of your code remains unchanged)

# Counter for image filenames
frame_counter = 0

# Function to draw a petal with a specified line shape and thickness
def draw_petal(radius, line_shape, line_thickness):
    turtle.width(line_thickness)

    if line_shape == 'square':
        for _ in range(4):
            turtle.forward(radius * 2)
            turtle.right(90)
    elif line_shape == 'rectangle':
        turtle.forward(radius * 2)
        turtle.right(90)
        turtle.forward(radius)
        turtle.right(90)
        turtle.forward(radius * 2)
        turtle.right(90)
        turtle.forward(radius)
        turtle.right(90)
    elif line_shape == 'curve':
        turtle.circle(radius, 180)
    elif line_shape == 'ellipse':
        for _ in range(2):
            turtle.circle(radius, 90)
            turtle.circle(radius / 2, 90)

# Function to draw text content at the top of the image
def draw_text_content(text_content):
    turtle.penup()
    turtle.goto(0, 250)  # Top of the image
    turtle.pendown()
    turtle.write(text_content, align="center", font=("Arial", 16, "normal"))

# Function to draw a lotus flower and capture frames
def draw_lotus(line_shape, line_thickness, text_content):
    turtle.speed(2)
    turtle.color("red")
    turtle.fillcolor("yellow")

    # Draw text content from the beginning
    draw_text_content(text_content)

    # Set starting position for petals at the center of the screen
    turtle.penup()
    turtle.goto(0, 0)
    turtle.pendown()

    # Draw the petals and capture frames
    for _ in range(12):
        draw_petal(100, line_shape, line_thickness)

        # Save the current frame as an image
        global frame_counter
        filename = f"{image_folder}/frame_{frame_counter:03d}.png"
        turtle.getcanvas().postscript(file=filename)
        img = Image.open(filename)
        img.save(filename)
        frame_counter += 1

        turtle.right(30)

    turtle.hideturtle()

# Fetch text content from MySQL table
def fetch_text_content():
    connection = mysql.connector.connect(**db_params)
    cursor = connection.cursor()

    query = "SELECT text_content FROM text ;"
    cursor.execute(query)
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result[0] if result else "Default Text"

# Draw the lotus flower with a specified line shape, thickness, and text content
text_content = fetch_text_content()
draw_lotus(line_shape=line_shape, line_thickness=line_thickness, text_content=text_content)

# Convert images to video using OpenCV
images = [f"{image_folder}/frame_{i:03d}.png" for i in range(frame_counter)]
frame = cv2.imread(images[0])
height, width, layers = frame.shape

# Create the VideoWriter with specified resolution and fps
video = cv2.VideoWriter(output_video, cv2.VideoWriter_fourcc(*'mp4v'), fps, video_resolution)

for image in images:
    frame = cv2.imread(image)

    # Resize the frame to the desired resolution
    frame = cv2.resize(frame, video_resolution)

    video.write(frame)

cv2.destroyAllWindows()
video.release()
