import os
import PySimpleGUI as sg
from PIL import Image, ImageDraw, ImageFont

# Get the current directory
current_dir = os.getcwd()

# Define the path to the file that will store the last used directory
directory_file = 'last_directory.txt'

# Check if the file exists and read the last used directory from it
if os.path.exists(directory_file):
    with open(directory_file, 'r') as f:
        last_directory = f.read().strip()
else:
    last_directory = current_dir  # No directory has been selected yet, so use current

# Define the layout of the window
layout = [[sg.Text('Select the ski trail difficulty:')],
          [sg.Radio('Green', 'difficulty', key='Green'), 
           sg.Radio('Blue', 'difficulty', key='Blue'), 
           sg.Radio('Single Diamond', 'difficulty', key='Single Diamond', default=True), 
           sg.Radio('Double Diamond', 'difficulty', key='Double Diamond')],
          [sg.Text('Enter the ski trail name:'), sg.InputText(key='trail_name')],
          [sg.Text('Save Directory:'), sg.InputText(default_text=last_directory, key='directory'), sg.FolderBrowse('Browse')],
          [sg.Button('Submit', bind_return_key=True), sg.Button('Cancel')]]


# Create the window and set the return_keyboard_events parameter to True
window = sg.Window('Ski Trail Submission Form', layout, return_keyboard_events=True)


# Event loop to process user inputs
while True:
    event, values = window.read()
    if event in (None, 'Cancel'):
        # Exit the program if the user closes the window or clicks Cancel
        break
    elif event == 'Submit' or event == 'Return:13':
        # Process the user's submission
        for difficulty in ['Green', 'Blue', 'Single Diamond', 'Double Diamond']:
            if values[difficulty]:
                difficulty_text = difficulty
                break
        trail_name = values['trail_name']
        directory = values['directory']
        print(f'Submitted: Difficulty = {difficulty_text}, Trail Name = {trail_name}')

        # Save the chosen directory to the file
        with open(directory_file, 'w') as f:
            f.write(values['directory'])

        # Close the window
        window.close()



# Load the original trail difficulty image
if difficulty_text == 'Green':
    image = Image.open('green.png').convert('RGBA')

elif difficulty_text == 'Blue':
    image = Image.open('blue.png').convert('RGBA')

elif difficulty_text == 'Single Diamond':
    image = Image.open('single_diamond.png').convert('RGBA')

elif difficulty_text == 'Double Diamond':
    image = Image.open('double_diamond.png').convert('RGBA')    


# Define the trail_name and font
font = ImageFont.truetype("arial.ttf", 150)
text_color = (0, 0, 0)

# Calculate the width of the trail_name
bbox = font.getbbox(trail_name)
trail_namewidth, trail_nameheight = bbox[2], bbox[3]

# Calculate the width of the new image
new_width = image.width + trail_namewidth + 20

# Create a new image with transparent background
new_image = Image.new('RGBA', (new_width, image.height), (0, 0, 0, 0))

# Paste the original image on the left side of the new image
new_image.paste(image, (0, 0))

# Draw the trail_name on the right side of the new image
draw = ImageDraw.Draw(new_image)
x = image.width + 20
y = (image.height - trail_nameheight) // 2
draw.text((x, y), trail_name, font=font, fill=text_color)

# Save the new image as a PNG file
filename = os.path.join(directory, f'{trail_name}.png')
new_image.save(filename, format='png')