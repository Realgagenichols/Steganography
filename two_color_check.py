from PIL import Image
from sys import argv


twoColorImage = argv[1]
image = Image.open(twoColorImage)
count = 0

cWidth, cHeight = image.size

numPixels = cWidth*cHeight

color1, color2 = 0, 0

# grab a pixel and store its color
firstColor = image.getdata()[1]

# find a pixel of a different color
for pixel in image.getdata():

    if pixel != firstColor:
        secondColor = pixel
        break

# count the pixels of each color
for pixel in image.getdata():

    if pixel == firstColor:
        color1 += 1
    elif pixel == secondColor:
        color2 += 1

if( (color1 + color2) != numPixels):
    print("not two color image!")
else:
    print("Two color image!")