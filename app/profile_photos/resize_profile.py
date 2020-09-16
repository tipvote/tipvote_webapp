
from PIL import Image
import os
from app import db
from flask_login import current_user

basewidth_150 = 150

ext = ['.jpg', '.png', '.gif', '.png', '.jpeg', '.JPG']


def convert_profile_image(imagelocation, imagename):
    """
    convert to thumbnail when a user uplaods a folder
    """
    thelocationandimage = (os.path.join(imagelocation, imagename))
    img = Image.open(thelocationandimage)
    # gets base name
    thebasename = os.path.splitext(thelocationandimage)[0]
    extension = os.path.splitext(thelocationandimage)[1]

    # rename image
    newname_150 = thebasename + "_150"

    non_renamed_file = (os.path.join(thebasename + extension))
    renamed_file_large = (os.path.join(newname_150 + extension))

    # see if image is already small ...
    imagewidth = int(img.size[0])

    if int(imagewidth) > int(151):
        # large image convert ..
        # convert and save large image
        wpercent_large = (basewidth_150 / float(img.size[0]))
        hsize_large = int((float(img.size[1]) * float(wpercent_large)))
        img = img.resize((basewidth_150, hsize_large), Image.ANTIALIAS)
        imagesave_renamed_large = os.path.join(imagelocation, renamed_file_large)
        img.save(imagesave_renamed_large, subsampling=0, quality=100, optimize=True)
        os.chmod(imagesave_renamed_large, 0o775)

        # save images
        # large image - save new name for databases
        location_of_large_file = os.path.join(imagelocation, renamed_file_large)
        location_of_large_file = location_of_large_file[5:]
        current_user.profileimage = location_of_large_file

        if os.path.isfile(thelocationandimage):
            os.remove(thelocationandimage)

    else:
        # small image
        location_of_large_file = os.path.join(imagelocation, non_renamed_file)
        location_of_large_file = location_of_large_file[5:]
        current_user.profileimage = location_of_large_file

    db.session.add(current_user)

