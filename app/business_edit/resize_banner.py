from flask import \
    redirect, \
    url_for

from PIL import Image
import os
from app import db
from flask_login import current_user
from app.classes.business import Business

basewidth_1000 = 1000

ext = ['.jpg', '.png', '.gif', '.png', '.jpeg', '.JPG']


def convert_banner_image(imagelocation, imagename, business_id):
    """
    convert to thumbnail when a user uplaods a folder
    """
    thebiz = db.session.query(Business).filter(Business.id == business_id).first()
    if current_user.id != thebiz.user_id:
        return redirect(url_for('index'))
    thelocationandimage = (os.path.join(imagelocation, imagename))
    img = Image.open(thelocationandimage)
    # gets base name
    thebasename = os.path.splitext(thelocationandimage)[0]
    extension = os.path.splitext(thelocationandimage)[1]

    # rename image
    newname_1000 = thebasename + "_1000"

    non_renamed_file = (os.path.join(thebasename + extension))
    renamed_file_large = (os.path.join(newname_1000 + extension))

    # see if image is already small ...
    imagewidth = int(img.size[0])

    if int(imagewidth) > int(1001):
        # large image convert ..
        # convert and save large image
        wpercent_large = (basewidth_1000 / float(img.size[0]))
        hsize_large = int((float(img.size[1]) * float(wpercent_large)))
        img = img.resize((basewidth_1000, hsize_large), Image.ANTIALIAS)
        imagesave_renamed_large = os.path.join(imagelocation, renamed_file_large)
        img.save(imagesave_renamed_large, subsampling=0, quality=100, optimize=True)
        os.chmod(imagesave_renamed_large, 0o775)

        # save images
        # large image - save new name for databases
        location_of_large_file = os.path.join(imagelocation, renamed_file_large)
        location_of_large_file = location_of_large_file[5:]
        thebiz.bannerimage = location_of_large_file

        if os.path.isfile(thelocationandimage):
            os.remove(thelocationandimage)

    else:
        # small image
        location_of_large_file = os.path.join(imagelocation, non_renamed_file)
        location_of_large_file = location_of_large_file[5:]
        thebiz.bannerimage = location_of_large_file

    db.session.add(current_user)

