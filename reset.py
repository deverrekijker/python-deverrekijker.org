import os


def reset():
    p = os.path.dirname(os.path.realpath(__file__)) + '/data/data.json'
    if os.path.isfile(p): os.remove(p)
