from random import random
import copy

def _rand_filename(digits=6):
    return str(int(random() * (10**digits)))


def is_float_basic(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    except TypeError:
        return False
    return False


def mix(main, append):
    for key in append:
        if key in main:
            pass
        else:
            main[key] = append[key]
