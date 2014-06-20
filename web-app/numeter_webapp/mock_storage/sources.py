from random import random, randint, randrange, choice
from math import sin


def full_random(x, offset_y=None, min_y=None, max_y=None):
    """Make a random line with a +-5 by step."""
    offset_y = offset_y or randint(0, 50)
    min_y = min_y if min_y is not None else randint(-50, 50)
    max_y = max_y or randint(x, x + 50)
    for i in xrange(x):
        # Not less than min
        if offset_y <= min_y:
            yield min_y
            offset_y += randrange(0, 6, 0.1, float)
        # Not more than max
        elif offset_y >= max_y:
            yield max_y
            offset_y += randrange(-5, 0, 0.1, float)
        else:
            yield offset_y
            offset_y += randrange(-5, 6, 0.1, float)

def linear(x, step=1, offset_y=None, min_y=None, max_y=None):
    """Simple increasing line."""
    min_y = min_y if min_y is not None else randint(-50, 50)
    max_y = max_y or randint(min_y, 50+x)
    offset_y = offset_y or randint(min_y, max_y)
    # Increment by step
    for i in xrange(x):
        # Increase
        if i + offset_y <= max_y:
            yield i + offset_y
        # Not more than max
        else:
            yield max_y

def linear_decrease(x, step=-1, offset_y=None, min_y=None, max_y=None):
    """Simple increasing line."""
    min_y = min_y if min_y is not None else randint(-50, 50)
    max_y = max_y or randint(min_y, min_y + 50)
    offset_y = offset_y or randint(-50, 50)
    for i in xrange(x, -x, step):
        # Decrese
        if i + offset_y >= min_y:
            yield i + offset_y
        # Not more than max
        else:
            yield min_y

def sinus(x, offset_x=None, offset_y=None, amp=None, min_y=None, max_y=None):
    """Sinux method."""
    amp = amp or randint(1, 20)
    min_y = min_y if min_y is not None else randint(-50, 50)
    max_y = max_y or randint(x, x + 50)
    offset_x = offset_x or randint(min_y, 50)
    offset_y = offset_y or randint(min_y, 50)

    for i in ( float(j) for j in xrange(x)):
        val = sin(i + offset_y) * amp + offset_x
        if val <= min_y:
            yield min_y
        elif val >= max_y:
            yield max_y
        else:
            yield val

def random_func(*args, **kwargs):
    #funcs = [full_random, linear, linear_decrease, sinus]
    funcs = [full_random]
    func = choice(funcs)
    for i in func(*args, **kwargs):
        yield i

def delta_of(x, offset_y=None, max_x=None):
    offset_y = offset_y or randint(0, 50)
    max_x = max(x)
    for i in x:
        # Not more than max
        if i >= max_x:
            yield 0
        # Not less than zero
        elif i <= 0:
            yield max_x
        # Give delta between
        else:
            yield (max_x - i)


