# coding=utf-8
from random import randint

current_address = 'A1S3B3UCaT34HDFkUWcoTEd4qER8L47A865FN1z92kY5XdFidfdsunz4Yr7KBMHxjhFKEU4SkrFATas5i3sG7AFr9hziC1'


def randomwithndigits(n=64):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

