# Written by Gage Nichols

from PIL import Image # need to install pillow library for this to work
from sys import argv
#import numpy as np
#from math import sqrt

#############################################
#
# input - 2 color image
#
# Counts the number of pixels for 
# each of the two colors in the image. 
# Works for arbitrary colors and file 
# formats no need to be just B&W
#
# returns the one with the smaller count
# to use to be hidden and the count
#
#############################################
def countPixels(image):

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

    # return the color that appears least
    if color1 > color2:
        return secondColor, color2
    elif color1 < color2:
        return firstColor, color1
    else:
        print('Even color distribution\n')
        return firstColor, color1 #unlikely edge case color returned doesnt matter since equal


#############################################
#
# inputs
# - image object
#
# turn in the image into an RGB list
#
#############################################
def toArr(image):

    colorArr = []
    
    for pixel in image.getdata():
        if pixel == (255,255,255):
            pixel = (254,254,254)
        colorArr.append(pixel)
    
    return colorArr

#############################################
#
# inputs
# - image object
#
# turn in the message image into an RGB list
#
#############################################
def toArrMessage(image): # possibly merge with toArr() function -- similar functionality

    pixelArr = []

    for pixel in image.getdata():
        if pixel == 0 or pixel == (0,0,0):
            pixelArr.append((0,0,0))
        elif pixel == 1 or pixel == 255 or pixel == (255,255,255):
            pixelArr.append((255,255,255))

    return pixelArr

#############################################
#
# inputs
# - RGB list
#
# split the RGB value and append each value
# seperately to a new list
#
#############################################
def toBytes(colorArr): # sidenote - not actually bytes but sets up for bytes()
    imArr = []
    for i in colorArr:
        r1,g1,b1 = i
        imArr.append(r1)
        imArr.append(g1)
        imArr.append(b1)
    return imArr


#############################################
#
# inputs
# - image object
#
# Checks if the image is a true 2 color image
#
#############################################
def checkTwoColor(image):

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
        return False
    else:
        return True

#############################################
#
# inputs
# - image object
#
# change color image to B&W
#
#############################################
def toBW(image):

    imArr = toArr(image)

    imSize = image.size

    for i in range(0,len(imArr)):
        r,g,b = imArr[i]
        if((r+g+b) < 384):
            imArr[i] = (0,0,0)
        else:
            imArr[i] = (255,255,255)
    #bytesArr = bytes(toBytes(imArr))
    #stegImage = Image.frombytes("RGB", imSize, bytesArr)
    #stegImage.show()
    
    return imArr


#############################################
#
# inputs
# - list of seperated RGB values
# - size in shape (width, height)
#
# create the image from the list and dispay it
#
#############################################
def showImage(arr, size): # not used but im scared to delete it -- good template
    bytesArr = bytes(arr)
    newImage = Image.frombytes("RGB", size, bytesArr)
    newImage.show()


#############################################
#
# inputs
# - color least found in 2 color message image
# - coverImage image object
# - messageImage image object
#
# hide the message image in the cover image
#
#############################################
def hideImage(leastColor, coverImage, messageImage):

    # convert images to lists of RGB values
    coverArr = toArr(coverImage)
    messageArr = toArrMessage(messageImage)


    mSize = messageImage.size # sizeof(messageImage)


    # extract from tuple
    width, height = mSize

    # cast to strings to left pas with zeros
    width = str(width)
    width = width.zfill(4)
    height = str(height)
    height = height.zfill(4)


    # holds the indexes of the leastColor in messageImage
    indexes = []

    # leastColor needs to be full RGB value
    if leastColor == 0:
        leastColor = (0,0,0)
    elif leastColor == 1 or leastColor == 255:
        leastColor = (255,255,255)

    # fill indexes[] with positions of least color in messageImage
    count = 0
    for pixel in messageArr:
        count = count + 1
        if pixel == leastColor:
            indexes.append(count)


    # in list of coverImage RGB values at indexes[] positions change to leastColor
    for index in indexes:
        coverArr[index] = leastColor

    # turn width & height into 4 2-digit nums for 
    w1 = int(width[:2])
    w2 = int(width[2:])
    h1 = int(height[:2])
    h2 = int(height[2:])

    # length of list
    length = len(coverArr)

    # replace last two pixel tuples with width and height
    coordinates = (w2,h1,h2)
    coverArr[length-1] = coordinates
    foo, bar, temp = coverArr[(length-2)]
    coordinates = (foo,bar, w1)
    coverArr[(length-2)] = coordinates

    # show and save image
    bytesArr = bytes(toBytes(coverArr))
    stegImage = Image.frombytes("RGB", coverImage.size, bytesArr)
    stegImage.show()
    stegImage.save("steg.bmp")

#############################################
#
# inputs
# - image object
#
# hidden data is either black or white so 
# scan the image and return the color with
# the greater count this will be the hidden 
# data to be extracted
#
# returns True if black and False if white
#
#############################################
def findExtract(image): # this works but is it ideal? What if hiding red? If shading works irrelevant?
    countBlack = 0
    countWhite = 0

    for pixel in image.getdata():
        if(pixel == (0,0,0) or pixel == 0):
            countBlack = countBlack + 1
        elif(pixel == (255,255,255) or pixel == 255):
            countWhite = countWhite + 1
    if countBlack > countWhite: return True
    if countWhite > countBlack: return False

#############################################
#
# inputs
# - image object
# - bg background color for the image
# - hWidth width of image to be extracted
# - hHeight height of image to be extracted
#
# create a new image using the hidden data 
# in the image, this image should be the
# same as the message image originally
# hidden in the cover image 
#
#############################################
def revealImg(image):
    
    size = getHiddenSize(image)

    hWidth, hHeight = size

    count = 0
    indexes = []

    # default hidden color is black
    imgPixels = (0,0,0)

    # default background is white
    bg = (255,255,255)

    # if hidden pixels are black get indexes of all black pixels in cover
    if(findExtract(image) == True):
        for pixel in image.getdata():
            count = count + 1
            if pixel == (0,0,0):
                indexes.append(count)
    # if hidden pixels are white get indexes of all white pixels in cover
    elif(findExtract(image) == False):
        bg = (0,0,0)
        imgPixels = (255,255,255)
        for pixel in image.getdata():
            count = count + 1
            if pixel == (255,255,255):
                indexes.append(count)
    

    
    # create the list that will construct the image background
    newImageArr = [bg]*hWidth*hHeight

    # for all the pixels of hidden color that would fit in the hidden image
    # plot them onto the background that was created
    for index in indexes:
        if index < len(newImageArr):
            newImageArr[index] = imgPixels
            
    
    # create the image, show it, and save it
    bytesArr = bytes(toBytes(newImageArr))
    stegImage = Image.frombytes("RGB", size, bytesArr)
    stegImage.show()
    stegImage.save("hiddenImage.bmp") # FUTURE IDEA ***** read in a name for this on the CLI -- not a priority


#############################################
#
# inputs
# - image object (open)
#
# extract the width x height from the image 
# found in the last two pixels
#
#############################################
def getHiddenSize(image):

    #convert image to a list
    imArr = toArr(image)

    # variable for the length of the list
    length = len(imArr)

    # last item in the list
    size = imArr[length-1]
    # second to last item in the list
    size1 = imArr[length-2]

    #split into individual numbers from tuple
    w2,h1,h2 = size
    foo, bar, w1 = size1

    # concat individual numbers into width and heighy
    width = int(str(w1)+str(w2))
    height = int(str(h1)+str(h2))

    # create a tuple of size 
    dimensions = (width,height)

    return dimensions


    


#############################################
#
# Main for running program
#
#############################################
def main():

    flag = 99

    try:
        # help message shown if passed -h or -help
        if (argv[1] == "-h" or argv[1] == "-help"):
            print(" _____ _______ ______ _____ ")
            print("/ ____|__   __|  ____/ ____|")
            print("| (___   | |  | |__ | |  __ ")
            print(" \___ \  | |  |  __|| | |_ |")
            print(" ____) | | |  | |___| |__| |")
            print("|_____/  |_|  |______\_____|")
            print("\nHIDE ----------------")
            print("This is indicated by the -hide flag")
            print("-cover indicates the cover image")
            print("-message indicates the message image to be hidden")
            print("Usage: project.py -hide -cover <cover image> -message <message image>\n")
            print("EXTRACTION ----------------")
            print("This is indicated by the -extract flag")
            print("The image follows the -extract")
            print("Usage: project.py -extract <image> \n")
            exit()
                
        else:

            # read in args based on flags from CLI
            for i in range(len(argv)):
                # hiding will be done
                if argv[i] == "-hide":
                    flag = 0 # flag swicthed to indicate hiding 

                    
                # read cover image
                if argv[i] == "-cover":
                    cover = argv[i+1]

                # read message image
                if argv[i] == "-message":
                    # store args in vars
                    twoColorImage = argv[i+1]
                        
                # image extracting is to be done
                if argv[i] == "-extract":
                    flag = 1 # flag to indicate extracting
                    img = argv[i+1] # image to extract informatrion from

                        

        # if hiding is to be accomplished
        if(flag == 0):
            # open necessary images 
            coverImage = Image.open(cover)
            messageImage = Image.open(twoColorImage)

            # store image sizes into vars
            cWidth, cHeight = coverImage.size
            mWidth, mHeight = messageImage.size
            mSize = messageImage.size

            # ensure the message image is a true 2-color image
            # if not make it one
            if(checkTwoColor(messageImage) != True):
                imArr = toBW(messageImage)
                messageImage.close()
                bytesArr = bytes(toBytes(imArr))
                messageImage = Image.frombytes("RGB", mSize, bytesArr)
            

            # value of the least present color in two color image
            # the count of that color in the image // currently unused but saved for future versions
            leastColor, leastColorCount = countPixels(messageImage)


            # ensure picture sizes are compatible
            if ((cWidth-2 < mWidth) or (cHeight-2 < mHeight)):
                print("\n\nYour cover image must be greater than or equal to your message image in both height and width.\n\n")
                exit() 

            

            # hide the message image in the cover
            # FUTURE IDEA ***** use CLI to takein name of output image and pass to hideImage()
            hideImage(leastColor, coverImage, messageImage)

            # close images after operations      
            coverImage.close()
            messageImage.close()

        # reveal the hidden message image from the cover and save
        elif(flag == 1 ):
            stegImg = Image.open(img)
            revealImg(stegImg)
            stegImg.close()
        else:
            print("Please indicate hiding or extracting: -help for more information")
    except:
        print("Use -help for more information")



main()
