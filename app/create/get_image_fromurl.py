import requests
from PIL import Image
import os
from app import db
from app.common.functions import mkdir_p, random_image_name

basewidth_600 = 600

ext = ['.jpg', '.png', '.gif', '.png', '.jpeg', '.JPG', '.webp']


def getimage(url, imagelocation, thepost):
    """
    gets the image when a url is given
    """
    try:
        theurl = str(url)
        filename = url.split('/')[-1]
        r = requests.get(theurl, allow_redirects=False)
        mkdir_p(imagelocation + '/')
        thelocationandimage = (os.path.join(imagelocation + '/' + filename))
        thebasename = str(random_image_name())
        open(thelocationandimage, 'wb').write(r.content)
        extension = os.path.splitext(thelocationandimage)[1]
        newname_600 = thebasename + "_600"

        if extension == '.gif':
            non_renamed_file = (os.path.join(thebasename + extension))
            location_of_large_file = os.path.join(imagelocation, non_renamed_file)
            location_of_large_file = location_of_large_file[13:]
            thepost.url_image_server = location_of_large_file

        else:
            img = Image.open(thelocationandimage)

            if extension not in ext:
                img = img.convert('RGB')
                newextension = '.jpg'
                non_renamed_file = (os.path.join(thebasename + newextension))
                renamed_file_large = (os.path.join(newname_600 + newextension))
            else:
                non_renamed_file = (os.path.join(thebasename + extension))
                renamed_file_large = (os.path.join(newname_600 + extension))

            # save file
            imagesave = os.path.join(imagelocation, non_renamed_file)
            img.save(imagesave, subsampling=0, quality=95, optimize=True)
            os.chmod(imagesave, 0o775)

            imagewidth = int(img.size[0])
            if int(imagewidth) > int(551):
                # CONVERT
                # LARGE IMAGE

                # convert and save large image
                wpercent = (basewidth_600 / float(img.size[0]))
                hsize = int((float(img.size[1]) * float(wpercent)))
                img = img.resize((basewidth_600, hsize), Image.ANTIALIAS)
                imagesave = os.path.join(imagelocation, renamed_file_large)
                img.save(imagesave, subsampling=0, quality=95, optimize=True)
                os.chmod(imagesave, 0o775)

                # large file - get name and set for database
                location_of_large_file = os.path.join(imagelocation, non_renamed_file)
                location_of_large_file = location_of_large_file[13:]

                if location_of_large_file is None:
                    thepost.url_image_server = ''
                else:
                    thepost.url_image_server = location_of_large_file

                if os.path.isfile(thelocationandimage):
                    os.remove(thelocationandimage)
            else:
                # SMALL FILE
                # DONT CONVERT
                # large file - get name and set for database
                location_of_large_file = os.path.join(imagelocation, non_renamed_file)
                location_of_large_file = location_of_large_file[13:]

                if location_of_large_file is None:
                    thepost.url_image_server = ''
                else:
                    thepost.url_image_server = location_of_large_file
    except:
        thepost.url_image_server = ''

    db.session.add(thepost)
