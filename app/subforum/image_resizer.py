
from PIL import Image
import os

basewidth_150 = 100


ext = ['.jpg', '.png', '.gif', '.png', '.jpeg', '.JPG']


def convertimage(imagelocation, imagename):
    # convert to thumbnail
    thelocationandimage = (os.path.join(imagelocation, imagename))
    img = Image.open(thelocationandimage)
    # gets base name
    thebasename = os.path.splitext(thelocationandimage)[0]
    extension = os.path.splitext(thelocationandimage)[1]
    # rename image
    newname_150 = thebasename + "_150x150"

    non_renamed_file = (os.path.join(thebasename + extension))
    renamed_file = (os.path.join(newname_150 + extension))

    # convert and save
    wpercent = (basewidth_150 / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((basewidth_150, hsize), Image.ANTIALIAS)
    imagesave_renamed = os.path.join(imagelocation, renamed_file)
    img.save(imagesave_renamed, subsampling=0, quality=95, optimize=True)
    os.chmod(imagesave_renamed, 0o775)

    # save new name
    location_of_large_file = os.path.join(imagelocation, non_renamed_file)
    # location_of_large_file = location_of_large_file[10:]
    os.remove(location_of_large_file)
    location_of_thumbnail_file = os.path.join(imagelocation, renamed_file)
    location_of_thumbnail_file = location_of_thumbnail_file[5:]

    return location_of_thumbnail_file
