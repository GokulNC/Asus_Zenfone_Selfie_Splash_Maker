## Created By Gokul NC

#===========================================================================

#  This script reads the pictures and creates the splash.img for Asus Zenfone, tested to be working on Zenfone Selfie & Zenfone 2 Laser

## This is for Asus Zenfone device only, please do not try on other devices, unless you know what you're doing..

# /*
# Environment requirement:
#     Python + PIL
#     PIL install:
#         (ubuntu)  sudo apt-get install python-imaging
#         (windows) (http://www.pythonware.com/products/pil/)

# Limits:
#    a. This script only support Python 2.7.x, 2.6.x,
#      Can't use in py3x for StringIO module
#    b. This script's input can be a png, jpeg, bmp, gif file.
#    But if it is a gif, only get the first frame by default.
#
# Description:
#    1) STRUCTURE OF LOGO_HEADER: (Header size: 512 bytes)
#
#       For each image (32bytes):             (All Numbers are stored in Little Endian Format)
#           char[16] picture_name;  //16bytes - Name of the picture, stored in list_of_images[i][0]
#           unsigned offset         // 4bytes - the offset block from where picture payload begins; stored in list_of_images[i][1] (1block = 512bytes) (for e.g., for first picture, offset = 512/512 = 1)
#           unsigned blocks;        // 4bytes - number of blocks consumed, that is, (size of image payload in bytes)/512; stored in list_of_images[i][2]
#           unsigned width;         // 4bytes - picture's width; stored in list_of_images[i][3]
#           unsigned height;        // 4bytes - picture's height; stored in list_of_images[i][4]
#           
#       This is repeated for each picture
#
#    2) STRUCTURE OF PAYLOAD_DATA:
#        
#        Each pixel takes 3 bytes each in the format: [b, g, r] (This is called bgr24)
#        (It's stored as bgr24 instead of rgb24 because the processor is little endian, so bgr is read as rgb)
#       
#       
#    The Final splash.img Layout:
#       logo_header (512bytes) + Payload_data

# ===========================================================================*/
from __future__ import print_function
import sys,os
import struct
import StringIO
from PIL import Image

SUPPORTED_FORMATS = ["png", "jpg", "jpeg", "bmp", "gif"]

NUMBER_OF_IMAGES = 8

# Do not change these names!!
IMAGE_NAMES = ["ASUS_logo_HD", "batt_crit_FHD",
               "battery_charge", "android_FHD",
               "batt_charge_FHD", "battery_crit",
               "android_HD", "ASUS_logo_FHD"]


## get header
def GetImgHeader(list_of_images):
    SECTOR_SIZE_IN_BYTES = 512   # Header size
    header = [0 for i in range(SECTOR_SIZE_IN_BYTES)]

    current_offset = 0
    
    for image in list_of_images:
        
        # Name of the image
        header[current_offset:current_offset+16] = image[0][:16]
        current_offset += 16
        
        # Convert all values to little-endian:
        
        # Offset Sector of image
        header[current_offset]   = ( image[1]        & 0xFF)
        header[current_offset+1] = ((image[1] >> 8 ) & 0xFF)
        header[current_offset+2] = ((image[1] >> 16) & 0xFF)
        header[current_offset+3] = ((image[1] >> 24) & 0xFF)
        current_offset += 4
        
        # Number of sectors of payload in image
        header[current_offset]   = ( image[2]        & 0xFF)
        header[current_offset+1] = ((image[2] >> 8 ) & 0xFF)
        header[current_offset+2] = ((image[2] >> 16) & 0xFF)
        header[current_offset+3] = ((image[3] >> 24) & 0xFF)
        current_offset += 4
        
        # Width of image
        header[current_offset]   = ( image[3]        & 0xFF)
        header[current_offset+1] = ((image[3] >> 8 ) & 0xFF)
        header[current_offset+2] = ((image[3] >> 16) & 0xFF)
        header[current_offset+3] = ((image[3] >> 24) & 0xFF)
        current_offset += 4
        
        # Height of image
        header[current_offset]   = ( image[4]        & 0xFF)
        header[current_offset+1] = ((image[4] >> 8 ) & 0xFF)
        header[current_offset+2] = ((image[4] >> 16) & 0xFF)
        header[current_offset+3] = ((image[4] >> 24) & 0xFF)
        current_offset += 4
    
    header[SECTOR_SIZE_IN_BYTES-1] = NUMBER_OF_IMAGES
    
    output = StringIO.StringIO()
    for i in header:
        output.write(struct.pack("B", i))
    content = output.getvalue()
    output.close()
    return content

def convert_to_ascii(text, length):
    ascii = [ord(char) for char in text]
    while len(ascii)<length:
        ascii.append(0)
    return ascii

## get payload data : BGR Interleaved
def GetImageBody(img):
    color = (0, 0, 0)
    if img.mode == "RGB":
        background = img
    elif img.mode == "RGBA":
        background = Image.new("RGB", img.size, color)
        img.load()
        background.paste(img, mask=img.split()[3]) # alpha channel
    elif img.mode == "P" or img.mode == "L":
        background = Image.new("RGB", img.size, color)
        img.load()
        background.paste(img)
        #background.save("splash.png")
    else:
        print ("sorry, can't support this format")
        sys.exit()
    
    background.load()
        
    r, g, b = background.split()
    return Image.merge("RGB",(b,g,r)).tostring()

## make a image
def MakeImage(logo, out, mode):
    img = Image.open(logo)
    file = open(out, mode)
    body = GetImageBody(img)
    #file.write(GetImgHeader(img.size, len(body)))
    number_of_bytes = int(len(body))
    
    # No. of bytes of payload should be a multiple of 512 (since in flash memories, the minimum cluster size is 512bytes, which means 512bytes of data is read at each read)
    while number_of_bytes%512 != 0:
        body += "\0"
        number_of_bytes += 1
    
    file.write(body)
    file.close()
    width, height = img.size
    return [number_of_bytes/512, width, height]


## Get Valid File Name
def GetImageFile(filename):
    directory = "./pics/"
    infile = "" 
    for extension in SUPPORTED_FORMATS:
        infile = directory+filename+"."+extension
        if os.path.isfile(infile):
            return infile
        
    print("'"+filename+"' picture doesnot exist")
    sys.exit(); # error file


def AttachHeader(images_metadata, payload_file, output_file):
    
    with open(payload_file, "rb") as payload: data = payload.read()
    with open(output_file,  "wb") as output : output.write(GetImgHeader(images_metadata) + data)
    

##MAIN
if __name__ == "__main__":
    
    payload_file = "temp/payload.img"
    if len(sys.argv) >=2: output_file = sys.argv[1]
    else:                 output_file = "output/splash.img"
    
    if os.path.exists(payload_file):
        os.remove(payload_file)
    
    list_of_images = [[0 for j in range(5)] for i in range(NUMBER_OF_IMAGES)] #2D Array, with each row representing each image's metadata
    for i in range(NUMBER_OF_IMAGES):
        list_of_images[i][0] = convert_to_ascii(IMAGE_NAMES[i], 16)
    
    current_offset_sector = 1
    for i in range(NUMBER_OF_IMAGES):
        list_of_images[i][1] = current_offset_sector
        list_of_images[i][2:5] = MakeImage(GetImageFile(IMAGE_NAMES[i]), payload_file, "ab")
        current_offset_sector += list_of_images[i][2]
    
    AttachHeader(list_of_images, payload_file, output_file) # splash.img = Header + Payload