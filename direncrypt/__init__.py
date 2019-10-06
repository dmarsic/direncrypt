import os

ROOTDIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DATABASE = os.path.join(ROOTDIR, 'inventory.sqlite')
