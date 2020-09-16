
from PIL import Image
import os
from app import db


basewidth_1280 = 1280

ext = ['.jpg', '.png', '.gif', '.png', '.jpeg', '.JPG', '.webp']


def convertimage(imagelocation, imagename, thepost):
    """
    convert to thumbnail when a user uplaods a folder
    """
    try:
        thelocationandimage = (os.path.join(imagelocation, imagename))
        thebasename = os.path.splitext(thelocationandimage)[0]
        extension = os.path.splitext(thelocationandimage)[1]

        if extension == '.gif':
            location_of_large_file = thelocationandimage[5:]
            thepost.image_server_1 = location_of_large_file
        else:

            img = Image.open(thelocationandimage)
            try:
                if hasattr(img, '_getexif'):
                    exifdata = img.getexif()
                    orientation = exifdata.get(274)
                else:
                    orientation = 1
            except Exception as e:
                orientation = 1

            if orientation == 1:  # Horizontal (normal)
                pass
            elif orientation == 2:  # Mirrored horizontal
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 3:  # Rotated 180
                img = img.rotate(180)
            elif orientation == 4:  # Mirrored vertical
                img = img.rotate(180).transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 5:  # Mirrored horizontal then rotated 90 CCW
                img = img.rotate(-90).transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 6:  # Rotated 90 CCW
                img = img.rotate(-90)
            elif orientation == 7:  # Mirrored horizontal then rotated 90 CW
                img = img.rotate(90).transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 8:  # Rotated 90 CW
                img = img.rotate(90)
            else:
                pass

            img.save(thelocationandimage)

            # rename image
            newname_1280 = thebasename + "_1280"

            non_renamed_file = (os.path.join(thebasename + extension))
            renamed_file_large = (os.path.join(newname_1280 + extension))

            # see if image is already small ...
            imagewidth = int(img.size[0])

            if int(imagewidth) > int(1281):
                # large image convert ..
                # convert and save large image
                wpercent_large = (basewidth_1280 / float(img.size[0]))
                hsize_large = int((float(img.size[1]) * float(wpercent_large)))
                img = img.resize((basewidth_1280, hsize_large), Image.ANTIALIAS)
                imagesave_renamed_large = os.path.join(imagelocation, renamed_file_large)
                img.save(imagesave_renamed_large, subsampling=0, quality=100, optimize=True)
                os.chmod(imagesave_renamed_large, 0o775)

                # save images
                # large image - save new name for databases
                location_of_large_file = os.path.join(imagelocation, renamed_file_large)
                location_of_large_file = location_of_large_file[5:]
                thepost.image_server_1 = location_of_large_file

            else:
                # small image
                location_of_large_file = os.path.join(imagelocation, non_renamed_file)
                location_of_large_file = location_of_large_file[5:]
                thepost.image_server_1 = location_of_large_file

        db.session.add(thepost)

    except Exception as e:
        pass