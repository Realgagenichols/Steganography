from PIL import Image
from sys import argv
 

red = argv[1]
green = argv[2]
blue = argv[3]
name = argv[4]

imName = name + ".bmp"

rgb = (int(red),int(green),int(blue))

colorArr = [rgb]*1920*1080

imArr = []

size = (1920,1080)

for i in colorArr:
        r1,g1,b1 = i
        imArr.append(r1)
        imArr.append(g1)
        imArr.append(b1)

bytesArr = bytes(imArr)
newImage = Image.frombytes("RGB", size, bytesArr)
newImage.show()
newImage.save(imName)