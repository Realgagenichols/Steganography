from PIL import Image  # need to install pillow library for this to work
from sys import argv

CheckImage = argv[1]
image = Image.open(CheckImage)
countBlack = 0
countWhite = 0

for pixel in image.getdata():
    if(pixel == (0,0,0) or pixel == 0):
        countBlack = countBlack + 1
    elif(pixel == (255,255,255) or pixel == 255):
        countWhite = countWhite + 1

print("Number of black pixels: " + str(countBlack))
print("Number of white pixels: " + str(countWhite))