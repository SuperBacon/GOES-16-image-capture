import urllib
import json
import os
import shutil
from PIL import Image
import math


zoomLevel = 2 # zoom level can be set between 1 and 4
temporaryDirectoryName = 'temp_images' # the directory where the temporary images are stored
outputDirectoryName = 'output' # the folder where the files are outputted to
removeTemporyFiles = True # if the files should be removed


imageGridSizeX = int(math.pow( 2, zoomLevel ))
imageGridSizeY = int(math.pow( 2, zoomLevel ))

# gets the timestamps for the most recent clips
def getTimeStamps():
    print('Retrieving latest times...')
    link = "http://rammb-slider.cira.colostate.edu/data/json/goes-16/full_disk/geocolor/latest_times.json"
    file = urllib.urlopen(link)
    myfile = file.read()
    timestamps = json.loads(myfile)['timestamps_int']
    print( str(len(timestamps)) + ' timestamps found' )
    return timestamps

# checks if a directory exists, if it doesn't it creates on
def createDirectory( directoryName ):
    if not os.path.exists(directoryName):
        os.makedirs(directoryName)

# downloads a single image part
def downloadImagePart( imageUrl, imageName ):
    img = urllib.urlopen(imageUrl)
    localFile = open(imageName, 'wb')
    localFile.write(img.read())
    localFile.close()
    return img

# joins multiple image parts to one big image
def stitchImagesTogether( images, imageGridSizeX, imageGridSizeY, finalImageName ):

    print( '    Stitching together image ' + finalImageName )
    createDirectory( outputDirectoryName )

    if len(images) > 0:
        image = Image.open(images[0])
        width = image.width;
        height = image.height;

        result = Image.new('RGB', (width * imageGridSizeX, height * imageGridSizeY))
        index = 0;
        for y in range(imageGridSizeY):
            for x in range(imageGridSizeX):
                if len(images) > index:
                    imageA = Image.open(images[index])
                    result.paste(im=imageA, box=(x*width, y*height))
                index += 1;
        result.save(outputDirectoryName + '/' + finalImageName)

# gets the full images from an array of timestamps
def getImages( timestamps ):

    images = []
    for index, timestamp in enumerate(timestamps):
        filename = str(timestamp) + '.jpeg'
        if os.path.isfile( str(timestamp)+'.png' ):
            print('file ' + filename + ' already exists, skipping')
            continue
        print('')
        print('Image ' + str(index + 1) + '/' + str(len(timestamps)) + ' (' + filename + ')')
        count = 0
        for y in range(imageGridSizeY):
            for x in range(imageGridSizeX):
                image = 'http://rammb-slider.cira.colostate.edu/data/imagery/' + \
                    str(timestamp)[:8] + '/goes-16---full_disk/geocolor/' +  \
                    str(timestamp) + '/' + str(zoomLevel).zfill(2) + '/' + \
                    str(y).zfill(3) + '_' + str(x).zfill(3) + '.png'

                createDirectory(temporaryDirectoryName)

                imageName = temporaryDirectoryName + '/' + str(timestamp) + '_' + str(zoomLevel).zfill(2) + '_' + str(y).zfill(3) + '_' + str(x).zfill(3) + '.png'

                print('  downloading ' + str(count + 1) + '/' + str(imageGridSizeY * imageGridSizeX) + ' for ' + imageName )
                downloadImagePart(image, imageName)
                images.append(imageName)
                count += 1
        stitchImagesTogether(images, imageGridSizeX, imageGridSizeY, filename)
        images = []
        if removeTemporyFiles:
            print('      Removing tempory files')
            shutil.rmtree(temporaryDirectoryName)
            print('')


def generateMovie():
    os.system("ffmpeg -framerate 1 -pattern_type glob -i '*.png' video.mp4")

getImages( getTimeStamps() )
