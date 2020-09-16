import string
import random


def id_generator(size, chars=string.ascii_uppercase):

    return ''.join(random.choice(chars) for _ in range(size))
