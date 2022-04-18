# Steganography
Multiple scripts I wrote while studying steganography 

*** Need to install Python Pillow library to run the programs *** 

steg.py
Run with -h or -help to recieve a help message on usage

Usage:
For hiding 
project.py -hide -cover <cover image> -message <message image>

For extracting
project.py -extract <image>

Tech Write-up / basic idea
Hiding - message image is scanned and the two colors are counted - the lower count is returned
the indexes of the lower count pixels are saved to a list
everywhere in the cover image with an index on that list is replaced by a pixel with the lower count color
the dimensions of the message image are then preserved by hiding in the last 2 pixels - safe because the program will not attempt to hide a message image larger than the cover
How this works:
480x270 broken up into -> 04,80,02,70   ------ last two pixels of cover (x,x,x),(x,x,x) -> (x,x,04),(80,02,70)
Outputs image 'steg.bmp' with hidden data

Extraction - the size of the message is extracted from the last two pixels 
the image is scanned for black and white pixels the one with the higher count is hidden data so the opposite is chosen for a background color
a list of the size of the hidden image is created and populated with the rgb values of the background to create a blank canvas to paint the image on
the image is scanned for the hidden image pixel color and the indexes saved
for every index - change the pixel on the blank canvas so that the hidden image appears
saved as 'hiddenImage.bmp'
  
Updated to convert full color images to black and white then hide them *******
  
  
  
genImage.py -- can generate an image of a solid color using genImage.py <red value> <green value> <blue value> <file name w/ no extension>
^^ There is NO error checking or comments in this code it's only purpose was to gen images that are slightly off from true color images
i.e. if you're hiding white pixels create a cover image of all (254,254,254) so no change is detectable 


two_color_check.py  -- This just tells you if a potential message image is actually 2 colors - now not necessary because the steg.py will just exit if not
This works by grabbing two different pixel colors, counting the number of each of those pixels and comparing it to the number of pixels in the image


count_pixels.py  -- counts the number of black and white pixels in an image and prints to console, I used this to test the extracted image to ensure it retained the same count of pixels
