import os
import random
import string
from decimal import Decimal


def genericprofile(path):
    user_id = str(path)
    cmd = 'cp /home/Agora/data/user/noprofile.png /home/data/user/' + user_id
    try:
        os.system(cmd)
    except OSError:  # Python >2.7
        pass


def mkdir_p(path):
    try:
        os.makedirs(path, 0o755)
    except OSError:  # Python >2.7
        if os.path.isdir(path):
            pass
        else:
            raise


def random_user_name_anon(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def random_image_name(size=40, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def id_generator_picture1(size=20, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def id_generator_picture2(size=20, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def id_generator_picture3(size=20, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def floating_decimals(f_val, dec):
    prc = "{:."+str(dec)+"f}" # first cast decimal as str
    return Decimal(prc.format(f_val))
