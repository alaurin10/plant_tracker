from PIL import Image

# Load the original image
image = Image.open('single_diamond.png')

# Resize the image to a width of 300 pixels while preserving the aspect ratio
width, height = image.size
aspect_ratio = height / width
new_width = 250
new_height = int(new_width * aspect_ratio)
resized_image = image.resize((new_width, new_height))

# Save the resized image as a PNG file
resized_image.save('resized.png')
