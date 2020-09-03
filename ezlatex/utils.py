from random import random
import copy


def rand_filename(digits=6):
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


def to_float(s):
    if isinstance(s, (str, int, float)):
        try:
            return float(s)
        except ValueError:
            return None
        except TypeError:
            return None
    return None


def mix(main, append):
    for key in append:
        if key in main:
            pass
        else:
            main[key] = append[key]
