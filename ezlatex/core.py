from pylatex import Document, Alignat
from random import random
import re


def _rand_filename(digits=6):
    return str(int(random() * (10**digits)))


def _to_exp(items):
    if isinstance(items, exp):
        return items
    if isinstance(items, (str, int, float)):
        return exp(items)
    if isinstance(items, (list, tuple)):
        res = []
        for item in items:
            if isinstance(item, exp):
                res.append(item)
            else:
                res.append(exp(item))
        return res
    raise TypeError("Cannot Convert to Expression")


def _clean_exp(items):
    if isinstance(items, exp):
        if isinstance(items.value, (float, int)):
            return items
        if isinstance(items.value, str):
            return exp(items.value.replace('\\', '').replace("{", "(").replace("}", ")"))
    if isinstance(items, (list, tuple)):
        res = []
        for item in items:
            if isinstance(item.value, str):
                res.append(exp(item.value.replace('\\', '').replace("{", "(").replace("}", ")")))
            else:
                res.append(item)
        return tuple(res)
    raise TypeError("Cannot Convert to Expression")


class latex:
    def __init__(self):
        pass

    def create(self):
        pass


class exp(latex):
    """ Expressions """

    """ Class Variables """
    count = 0
    DEF_VARIABLES = ["x", "y", "z", "w"]  # or x_1, x_2, x_3, notation in the future
    mode = 1  # 0 for basic, 1 for regular notation, 2 for latex

    def __init__(self, value=None, method=None, mtype=None, is_base=None):
        """
        Initializes Variable

        @:param: is_base - (bool) overrides default method of determining if the value is a variable
        """
        self.method = method
        self.mtype = mtype
        self.is_base = False

        if isinstance(value, tuple):
            self.value = value
        elif isinstance(value, list):
            self.value = tuple(value)

        elif isinstance(value, str):
            if value[0] == "\\":
                # auto protect from \delta times x becoming \deltax
                value = "{%s}" % value
            self.value = value
            self.is_base = True
        elif isinstance(value, (int, float)):
            self.value = str(value)
        elif isinstance(value, exp):
            self.value = value
            if self.method is None:
                self.method = "pro"  # protected (parenthesis)
        elif value is None:
            if exp.count < len(exp.DEF_VARIABLES):
                self.value = "x_{}".format(exp.count)
                self.is_base = True
                exp.count += 1

        if is_base is not None:
            self.is_base = is_base
        if self.value is None:
            raise TypeError("\"value\" keyword argument not in types [tuple, list, str, int, float, exp]")

    def __repr__(self):
        if self.method is None:
            return str(self.value)
        elif exp.mode == 0:
            if isinstance(self.value, tuple):
                return "%s%s" % (self.method, str(self.value))
            return "%s(%s)" % (self.method, str(self.value))
        elif exp.mode == 1:
            # special methods
            self.value = _clean_exp(self.value)
            if self.method is "pro":
                return "(%s)" % self.value
            elif self.method is "add":
                return "%s + %s" % self.value
            elif self.method is "sub":
                return "%s - %s" % self.value
            elif self.method is "mul":
                if self.value[0].is_base and not self.value[1].is_base:
                    return "%s%s" % tuple(reversed(self.value))
                if self.value[1].is_base:
                    return "%s%s" % self.value
                return "%s(%s)" % self.value
            elif self.method is "div":
                return "%s/%s" % self.value
            elif self.method is "pow":
                return "%s^%s" % self.value
            elif self.method is "neg":
                return "-%s" % self.value

            # mains
            elif self.mtype is "binf":
                return "%s(%s, %s)" % (self.method, self.value[0], self.value[1])
            elif self.mtype in ("binm", "bins", "binr"):
                return "%s %s %s" % (self.value[0], self.method, self.value[1])
            elif self.mtype in ("unaf", "unas"):
                return "%s(%s)" % (self.method, self.value)

            raise ValueError("Invalid Function \"{}\"".format(self.method))
        elif exp.mode == 2:
            # special methods
            if self.method is "pro":
                return "(%s)" % self.value
            elif self.method is "add":
                return "{%s+%s}" % self.value
            elif self.method is "sub":
                return "{%s-%s}" % self.value
            elif self.method is "mul":
                if self.value[0].is_base and not self.value[1].is_base:
                    return "{%s%s}" % tuple(reversed(self.value))
                if self.value[1].is_base:
                    return "{%s%s}" % self.value
                return "{%s(%s)}" % self.value
            elif self.method is "div":
                return "{\\frac{%s}{%s}}" % self.value
            elif self.method is "pow":
                return "{%s^%s}" % self.value
            elif self.method is "neg":
                return "{-%s}" % self.value
            else:
                if not self.method.startswith("\\") and not self.method in ["=", "<", ">"]:
                    self.method = "\\{}".format(self.method)
                if self.mtype is "binf":
                    return "{%s(%s, %s)}" % (self.method, self.value[0], self.value[1])
                elif self.mtype is "binm":
                    return "{%s %s %s}" % (self.value[0], self.method, self.value[1])
                elif self.mtype is "bins":
                    return "{%s{%s}{%s}}" % (self.method, self.value[0], self.value[1])
                elif self.mtype is "binr":
                    return "%s %s %s" % (self.value[0], self.method, self.value[1])
                elif self.mtype is "unaf":
                    return "{%s(%s)}" % (self.method, self.value)
                elif self.mtype is "unas":
                    return "{%s{%s}}" % (self.method, self.value)
                raise ValueError("Invalid Function \"{}\"".format(self.method))
        raise ValueError("Mode Unavailable")

    def create(self):
        original_mode = exp.mode
        exp.mode = 2
        doc = Document(_rand_filename())
        with doc.create(Alignat(numbering=False, escape=False)) as agn:
            agn.append(self.__repr__())
        doc.generate_pdf()
        exp.mode = original_mode

    @staticmethod
    def binary(inputs, method):
        """ f(a,b) notation and f(a,b) latex """
        return exp(_to_exp(inputs), method=method, mtype="binf")

    @staticmethod
    def mbinary(inputs, method):
        """ a f b notation and a f b latex"""
        return exp(_to_exp(inputs), method=method, mtype="binm")

    @staticmethod
    def sbinary(inputs, method):
        """ a f b notation and f{a}{b} latex"""
        return exp(_to_exp(inputs), method=method, mtype="bins")

    @staticmethod
    def comp(inputs, method):
        """ a comp b notation and a comp b latex"""
        return exp(_to_exp(inputs), method=method, mtype="binr")

    @staticmethod
    def unary(input, method):
        """ f(a) notation and f(a) latex """
        if isinstance(input, tuple):
            input = input[0]
        return exp(_to_exp(input), method=method, mtype="unaf")

    @staticmethod
    def sunary(input, method):
        """ f(a) notation and f{a} latex """
        if isinstance(input, tuple):
            input = input[0]
        return exp(_to_exp(input), method=method, mtype="unas")

    # binary operators
    def __add__(self, other):
        return exp.binary((self, other), method="add")

    def __radd__(self, other):
        return exp(other) + self

    def __mul__(self, other):
        return exp.binary((self, other), method="mul")

    def __rmul__(self, other):
        return exp(other) * self
    
    def __sub__(self, other):
        return exp.binary((self, other), method="sub")

    def __rsub__(self, other):
        return exp(other) - self

    def __truediv__(self, other):
        # not just exp.sbinary(..., "\\frac") because __repr__ should print div(a, b) not \frac(a, b)
        return exp.binary((self, other), method="div")

    def __rtruediv__(self, other):
        return exp(other) / self

    def __pow__(self, power, modulo=None):
        return exp.binary((self, power), method="pow")

    def __rpow__(self, other):
        return exp(other) ** self

    # unary operators

    # comparison operators
    def __eq__(self, other):
        return exp.comp((self, other), method="=")

    def __ne__(self, other):
        return exp.comp((self, other), method="neq")

    def __lt__(self, other):
        return exp.comp((self, other), method="<")

    def __gt__(self, other):
        return exp.comp((self, other), method=">")

    def __le__(self, other):
        return exp.comp((self, other), method="leq")

    def __ge__(self, other):
        return exp.comp((self, other), method="geq")

    def __neg__(self):
        return exp.unary(self, "neg")

    # binary statics

    # unary statics
    @staticmethod
    def sin(expr):
        return exp.unary(expr, "sin")

    @staticmethod
    def cos(expr):
        return exp.unary(expr, "cos")

    @staticmethod
    def tan(expr):
        return exp.unary(expr, "tan")

    @staticmethod
    def cot(expr):
        return exp.unary(expr, "cot")

    @staticmethod
    def csc(expr):
        return exp.unary(expr, "csc")

    @staticmethod
    def sec(expr):
        return exp.unary(expr, "sec")

    @staticmethod
    def log(expr):
        return exp.unary(expr, "log")

    @staticmethod
    def ln(expr):
        return exp.unary(expr, "ln")

    @staticmethod
    def sqrt(expr):
        return exp.sunary(expr, "sqrt")

    @staticmethod
    def deriv(expr_u, expr_v, n=1, partial=False):
        if not (isinstance(n, int) and n > 0):
            raise ValueError("Cannot take \"{}\"-th derivative".format(n))
        if isinstance(expr_v.value, str):
            dtype = "{\\delta}" if partial else "d"
            denom = exp("{}{}".format(dtype, expr_v.value))
            if n > 1:
                denom **= n
            top = exp(dtype)
            if n > 1:
                top **= n
            if isinstance(expr_u.value, str):
                numer = top * expr_u  # exp("d{}".format(expr_u.value))
                return numer / denom
            return top / denom * expr_u
        raise ValueError("Cannot take derivate with respect to \"{}\"".format(expr_v.value))

    @staticmethod
    def partial(expr_u, expr_v, n=1):
        return exp.deriv(expr_u, expr_v, n, partial=True)

    # comparison statics


class text(latex):
    def __init__(self, text):
        self.text = "\\text{}".format(text)

    def create(self):
        doc = Document(_rand_filename())
        with doc.create(Alignat(numbering=False, escape=False)) as agn:
            agn.append(self.text)
        doc.generate_pdf()


class line:
    def __init__(self, *exps):
        self.exps = exps

    def add(self, *exps):
        self.exps += exps


