import io
import PIL
import zipfile

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import pytesseract
import cv2 as cv
import numpy as np

# loading the face detection classifier
face_cascade = cv.CascadeClassifier(
    'Week Three/haarcascade_frontalface_default.xml')

# path to the zip file containing PNG images
zip_path = "Week Three/small_img.zip"

# drawing font
fnt = ImageFont.truetype(r'C:\Users\System-Pc\Desktop\calibri.ttf', 40)

# open zip and return a list of the images
def readImages(zip_path):

    images = []

    # create a ZipFile object
    with zipfile.ZipFile(zip_path, 'r') as zip_file:

        # loop through each file in the zip archive
        for file_name in zip_file.namelist():

            # check if the file is a PNG image
            if file_name.endswith('.png'):

                # read the PNG image as bytes
                png_bytes = zip_file.read(file_name)

                # create an Image object from the PNG bytes
                image = Image.open(io.BytesIO(png_bytes))

                # save image object
                images.append([file_name, image])

    # return image list
    return images

# filter image list based on keyword
def filterImage(image_lst, keyword):

    filter_image_lst = []

    for image in images:
        
        # extract text from image
        text = pytesseract.image_to_string(image[1])
        
        if keyword in text:
            filter_image_lst.append(image)
            print("Found image in: " + image[0])

    return filter_image_lst

# detect phases from identified images
def detectFaces(zip_path, filter_image_lst, face_cascade):

    # list of iamge name, image and detected faces
    face_lst = []

    with zipfile.ZipFile(zip_path, 'r') as zip_file:

        for file_name in zip_file.namelist():

            for name, image in filter_image_lst:
                
                # if the file have the same name as the name of the image where the keyword was detected
                if file_name == name:
                    # save image as png
                    image.save(name[10:])
                    # open image with OpenCV
                    cv_img = cv.imread(name[10:])
                    
                    # Convert the image to grayscale and apply histogram equalization
                    gray_img = cv.cvtColor(cv_img, cv.COLOR_BGR2GRAY)
                    gray_img = cv.equalizeHist(gray_img)

                    # Detect faces with adjusted parameters
                    faces = face_cascade.detectMultiScale(gray_img, scaleFactor=1.2, minNeighbors=3)
                    #faces = face_cascade.detectMultiScale(cv_img)

                    # draw image to show identified faces
                    drawing = ImageDraw.Draw(image)
                    # list of faces in image
                    image_face_lst = []

                    for x, y, w, h in faces:
                        # draw rectange of detected face
                        drawing.rectangle((x, y, x+w, y+h), outline="red")
                        # crop detected fist
                        face = image.crop((x, y, x + w, y + h))
                        # add face to face list
                        image_face_lst.append(face)
                    # add name, image and face list
                    face_lst.append([name, image, image_face_lst])
                    # show image and detected faces
                    image.show()
    return face_lst

def createImage(name, image, face_lst):
    if len(face_lst) != 0:
        # initialize variables
        faces_in_row = 5
        face_width = 120
        face_height = 120

        mode = face_lst[0].mode
        image_width = faces_in_row*face_width
        if len(face_lst) % faces_in_row == 0:
            image_height = (len(face_lst)//faces_in_row)*face_height + 50
        else:
            image_height = (len(face_lst)//faces_in_row + 1)*face_height + 50

        # create a new image that contains all identified faces
        contact_sheet = Image.new(mode, (image_width, image_height), color="white")

        # resize all faces
        resized_face_lst = []

        for face in face_lst:
            face = face.resize((face_width, face_height), PIL.Image.Resampling.LANCZOS)
            resized_face_lst.append(face)

        # populate new image
        x = 0
        y = 50

        # write information in image
        drawing_object = ImageDraw.Draw(contact_sheet)
        text = "Results found in file {}".format(name[10:])
        drawing_object.text((5, 5), text,
                            font=fnt, fill=(0, 0, 0, 128))

        first_image = resized_face_lst[0]

        for img in resized_face_lst:
            # Lets paste the current image into the contact sheet
            contact_sheet.paste(img, (x, y))
            # Now we update our X position. If it is going to be the width of the image, then we set it to 0
            # and update Y as well to point to the next "line" of the contact sheet.
            if x+first_image.width == contact_sheet.width:
                x = 0
                y = y+first_image.height
            else:
                x = x+first_image.width

        if x != contact_sheet.width:
            blank = Image.new(mode, (contact_sheet.width - x, image_height), color="black")

            contact_sheet.paste(blank, (x, y))
    else:

        mode = "RGB"
        image_width = 5 * 120
        image_height = 100

        # create a new image that contains all identified faces
        contact_sheet = Image.new(mode, (image_width, image_height), color="white")

        # write information in image
        drawing_object = ImageDraw.Draw(contact_sheet)
        text = "Results found in file {} \n But there were no faces in that file!".format(name[10:])
        drawing_object.text((5, 5), text,
                            font=fnt, fill=(0, 0, 0, 128))

        first_image = resized_face_lst[0]

        for img in resized_face_lst:
            # Lets paste the current image into the contact sheet
            contact_sheet.paste(img, (x, y))
            # Now we update our X position. If it is going to be the width of the image, then we set it to 0
            # and update Y as well to point to the next "line" of the contact sheet.
            if x+first_image.width == contact_sheet.width:
                x = 0
                y = y+first_image.height
            else:
                x = x+first_image.width

    return contact_sheet


# main
# read images
images = readImages(zip_path)

keyword = input("Enter a keyword: ")

filter_image_lst = filterImage(images, keyword)

faces_lst = detectFaces(zip_path, filter_image_lst, face_cascade)

face_sheets = []

sheet_height = 0

for faces in faces_lst:
    face_sheet = createImage(faces[0], faces[1], faces[2])
    face_sheet.show()
    face_sheets.append(face_sheet)

    sheet_height += face_sheet.height

first_image = face_sheets[0]

contact_sheet = Image.new(first_image.mode, (first_image.width, sheet_height), color="white")

x=0
y = 0

for img in face_sheets:
    # Lets paste the current image into the contact sheet
    contact_sheet.paste(img, (x, y))
    # Now we update our X position. If it is going to be the width of the image, then we set it to 0
    # and update Y as well to point to the next "line" of the contact sheet.
    y = y + img.height

contact_sheet.show()

print("Done")
