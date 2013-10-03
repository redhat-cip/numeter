from random import random, randint, randrange, choice
from math import sin

def full_random(x):
    """Make a random line with a +-5 by step."""
    val = random() * 100
    for i in xrange(x):
        yield val
        val += randrange(-5,6,0.1, float)

def linear(x, step=1, offset_y=None):
    """Simple increasing line."""
    offset_y = offset_y or randint(-50,50)
    for i in xrange(x):
        yield i + offset_y
        i += step

def linear_decrease(x, step=-1, offset_y=None):
    """Simple increasing line."""
    offset_y = offset_y or randint(-50,50)
    for i in xrange(x,-x,step):
        yield i + offset_y

def sinus(x, offset_x=None, offset_y=None, amp=None):
    """Sinux method."""
    offset_x = offset_x or randint(-50,50)
    offset_y = offset_y or randint(-50,50)
    amp = amp or randint(1,20)

    for i in ( float(j) for j in xrange(x)):
        yield sin(i + offset_y) * amp + offset_x

def random_func(x):
    funcs = [full_random,linear,linear_decrease,sinus]
    func = choice(funcs)
    for i in func(x):
        yield i
