import sys

PYTHON_VERSION = sys.version_info[0]


def printit(message, *args):
    """Internal method to print messages to STDOUT."""
    uargs = []
    for a in args:
        if PYTHON_VERSION == 2 and isinstance(a, basestring):
            a = a.encode('utf-8', errors='replace')
        uargs.append(a)
    print(message.format(*uargs))
