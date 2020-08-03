from pylatex import Document, Alignat, NoEscape
from random import random
import warnings
import copy
import functools
import math
from operator import mul

from .errors import *
from .utils import _rand_filename, is_float_basic, mix


def is_float(s):
    if isinstance(s, exp) and s.method is None:
        return is_float_basic(s.value)
    return is_float_basic(s)


def _get_value(expr):
    if isinstance(expr, (str, int, float)) and is_float(expr):
        return float(expr)
    elif isinstance(expr, exp) and is_float(expr):
        return float(expr.value)


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
    raise TypeError("Cannot Convert Type %s to Expression" % str(type(items)))


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
    return items
    # raise TypeError("Cannot Convert to Expression")


def sum_prod_evalf(vari, fro, to, expr, typef=sum, **kwargs):
    best_name = vari.name if vari.name is not None else vari.value
    if best_name in kwargs:
        raise TypeError("Cannot calculate sum with kwarg \"{}\" passed".format(best_name))
    if not is_float(fro):
        fro = fro(**kwargs)
    if not is_float(to):
        to = to(**kwargs)
    if is_float(fro) and is_float(to):
        l = []
        for i in range(int(_get_value(fro)), int(_get_value(to)) + 1, 1):
            kwargs[best_name] = i
            l.append(expr(**kwargs))
        return typef(l)
    raise TypeError("Cannot calculate sum/product from \"{}\" to \"{}\"".format(fro, to))


def factorial(n):
    try:
        n = int(n)
        if n < 0:
            raise TypeError()
    except TypeError:
        raise TypeError("Factorials can only take positive integers.")
    q = 1
    for i in range(2, n+1, 1):
        q *= i
    return q


def deriv_evalf(expr_u, expr_v, n, first=True, **kwargs):
    print(kwargs)
    raise DerivativeError("Sorry, I can't take the derivative of that")
    # curr = None
    # if first:
    #     warnings.warn("Derivative calculation is very basic!")
    # if is_float(expr_u):
    #     return 0
    # if expr_u.value == expr_v.value:
    #     return 1
    # if expr_u.method == "pow":
    #     # chain rule
    #     if expr_u.value[0].value == expr_v.value and is_float(expr_u.value[1].value):
    #         exponent = (expr_u.value[1] - 1)()
    #         return expr_u.value[1] * expr_v ** exponent * deriv_evalf(expr_u.value[0], expr_v, 1, False)
    # if expr_u.method == "mul":
    #     # product rule
    #     if expr_u.value
    # if curr is None:
    #     raise exp.DerivativeError("Sorry, I can't take the derivative of that")
    # if n == 1:
    #     return curr
    # return deriv_evalf(curr, expr_v, 1, first=False)


def partial_evalf(expr_u, expr_v, n, first=True):
    raise DerivativeError("Sorry, I can't take the derivative of that")


class latex:
    def __init__(self):
        pass

    def create(self, name=None):
        doc(line(self), name=name).create()

    def to_latex(self):
        """ to be defined in child classes """
        pass


class exp(latex):
    """ Expressions """

    """ Class Variables """
    count = 0
    DEF_VARIABLES = ["x", "y", "z", "w"]  # or x_1, x_2, x_3, notation in the future
    mode = 1  # 0 for basic, 1 for regular notation, 2 for latex

    def __init__(self, value=None, method=None, mtype=None, is_base=None, evalf=None, name=None, ignores_vars=False, force_value=None):
        """
        Initializes an expression.

        :param value: (tuple, str, int, float, exp) - any of the arguments normally passed to this method
            * if type(value) is another exp then this object acts as parenthesis in LaTeX
            * if type(value) is a str then this object is a variable
            * if value is None then this object is a new variable "x_n", where "n" keeps increasing as we make more
        :param method: (str) - method associated
            * if this object is a variable or number, method is irrelevant
        :param mtype: (str) - see __repr__
        :param is_base: (bool) - overrides default method of determining if the value is a variable
        :param evalf: (func) - function to call when evaluating. see __call__
        :param name:
        :param ignores_vars: (bool) - see __call__
        :param force_value: (int, float)
        """
        self.method = method
        self.mtype = mtype
        self.evalf = evalf
        self.name = name
        self.ignores_vars = ignores_vars
        self.is_base = False
        self.force_value = force_value
        self.call_kwargs = {}

        if isinstance(value, tuple):
            self.value = value
        elif isinstance(value, list):
            self.value = tuple(value)

        elif isinstance(value, str):
            if value[0] == "\\":
                # auto protect from \delta times x becoming \deltax
                if self.name is None:
                    self.name = value[1:]
                value = "{%s}" % value
            self.value = value
            self.is_base = True
        elif isinstance(value, (int, float)):
            self.value = value
            if value < 0:
                self.value = -exp(1)
                self.method = "pro"
        elif isinstance(value, exp):
            self.value = value
            if self.method is None:
                self.method = "pro"  # protected (parenthesis)
        elif value is None:
            if exp.count < len(exp.DEF_VARIABLES):
                self.value = "x_{}".format(exp.count)
                self.is_base = True
                exp.count += 1

        if is_float(self.value):
            self.is_base = False
        if is_base is not None:
            self.is_base = is_base
        if self.value is None:
            raise TypeError("\"value\" keyword argument not in types [tuple, list, str, int, float, exp]")

    def __call__(self, *args, **kwargs):
        """
        Evaluates all the functions recursively, using kwargs as variables if provided. If not all variables are pro-
        vided, it will evaluate as much as possible into the returned expression (warning the left-out variables).

        If this expression has ignores_vars=True, then __call__(*args, **kwargs) returns self.evalf(*args, **kwargs)
        without checking if all necessary variables have been defined (this is useful for higher order functions, like
        sigma, where the wrapper is essentially a for loop which calls the expression function several times -- here,
        we actually don't want the variable to be defined as we're looping over it)

        Otherwise, self.evalf can be a simple function like lambda x, y: x + y, and __call__ will evaluate all
        variables.

        If force_value is provided in the constructor, that integer will override the default value (i.e. a display as
        \\infty, but a value of 99, etc)

        i.e.
        > expr = exp.sin("x") + exp("r") * 3
        > expr(r=2)
        sin(x) + 6.0                <- this is an exp
        > exp(x=math.pi, r=2)
        6.0                         <- this is a float

        :param args: none expected
        :param kwargs: variables to be computed with
        :return: (float, exp) - float if all variables given, else exp
        """
        # mix(self.call_kwargs, kwargs)
        # kwargs = self.call_kwargs
        if self.method is None:
            # specials
            if self.force_value is not None:
                return self.force_value
            if self.name == "pi":
                return math.pi
            if self.name == "e":
                return math.e
            if self.name == "tau":
                return math.tau
            if self.name == "infty":
                return 9999999
            best_name = self.name if self.name else self.value
            if isinstance(best_name, str) and best_name in kwargs and is_float(kwargs[best_name]):
                return kwargs[best_name]
            return self.value
        if self.method == "pro":
            return self.value(*args, **kwargs)
        if self.evalf is not None:
            # special
            if self.ignores_vars:
                return self.evalf(*self.value, **kwargs)

            # unary
            if isinstance(self.value, (int, float, str)):
                if is_float(self.value):
                    return self.evalf(float(self.value))
                raise TypeError("Cannot convert \"{}\" to float".format(self.value))
            elif isinstance(self.value, exp):
                exp_value = self.value(*args, **kwargs)
                if is_float(exp_value):
                    return self.evalf(float(exp_value))
                best_name = self.value.name if self.value.name is not None else exp_value
                if isinstance(best_name, str) and best_name in kwargs and is_float(kwargs[best_name]):
                    return self.evalf(kwargs[best_name])
                try:
                    return self.evalf(self.value)
                except TypeError:
                    new_self = copy.deepcopy(self)
                    if isinstance(best_name, str):
                        warnings.warn("Need kwarg \"{}\" to evaluate fully".format(best_name))
                    return new_self
            # binary
            elif isinstance(self.value, (list, tuple)):
                args = []
                bad_kwargs = []
                for arg_exp in self.value:
                    if isinstance(arg_exp, (int, float, str)):
                        if is_float(arg_exp):
                            args.append(float(arg_exp))
                        else:
                            raise TypeError("Cannot convert \"{}\" to float".format(arg_exp))
                    elif isinstance(arg_exp, exp):
                        exp_value = arg_exp(*args, **kwargs)
                        if is_float(exp_value):
                            args.append(float(exp_value))
                        else:
                            best_name = arg_exp.method if arg_exp.name is not None else exp_value
                            if isinstance(best_name, str) and best_name in kwargs and is_float(kwargs[best_name]):
                                args.append(kwargs[best_name])
                            else:
                                new_arg_exp = copy.deepcopy(arg_exp)
                                args.append(new_arg_exp)
                                bad_kwargs.append(best_name)
                                if isinstance(best_name, str):
                                    warnings.warn("Need kwarg \"{}\" to evaluate fully".format(best_name))
                try:
                    return self.evalf(*args)
                except TypeError:
                    raise TypeError("Need kwargs ({}) to evaluate".format(", ".join(bad_kwargs)))
            return self.evalf(*args, **kwargs)
        raise NotImplementedError("Cannot evaluate \"{}\"".format(self.method))

    def eval(self, *args, **kwargs):
        return self(*args, **kwargs)

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
            elif self.method is "factorial":
                if self.value.is_base or is_float(self.value):
                    return "%s!" % self.value
                return "(%s)!" % self.value

            # mains
            elif self.mtype is "binf":
                return "%s(%s)" % (self.method, ", ".join(map(str, self.value)))
            elif self.mtype in ("binm", "bins", "binr"):
                return "%s %s %s" % (self.value[0], self.method, self.value[1])
            elif self.mtype in ("unaf", "unas"):
                return "%s(%s)" % (self.method, self.value)

            if isinstance(self.value, tuple):
                return "%s%s" % (self.method, str(self.value))
            return "%s(%s)" % (self.method, str(self.value))
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
            elif self.method is "nderiv":
                if self.value[0].is_base:
                    if int(self.value[2].value) == 1:
                        print("!")
                        return "{\\frac{\\textrm{d}%s}{\\textrm{d}%s}}" % (self.value[0], self.value[1])
                    return "{\\frac{\\textrm{d}^{%s}%s}{{\\textrm{d}%s}^{%s}}}" % (self.value[2], self.value[0], self.value[1], self.value[2])
                if int(self.value[2].value) == 1:
                    return "{\\frac{\\textrm{d}}{\\textrm{d}%s}(%s)}" % (self.value[1], self.value[0])
                return "{\\frac{\\textrm{d}^{%s}}{{\\textrm{d}%s}^{%s}}(%s)}" % (self.value[2], self.value[1], self.value[2], self.value[0])
            elif self.method is "npartial":
                if self.value[0].is_base:
                    if self.value[2].value == 1:
                        return "{\\frac{{\\delta}%s}{{\\delta}%s}}" % (self.value[0], self.value[1])
                    return "{\\frac{{\\delta}^{%s}%s}{{{\\delta}%s}^{%s}}}" % (self.value[2], self.value[0], self.value[1], self.value[2])
                if self.value[2].value == 1:
                    return "{\\frac{{\\delta}}{{\\delta}%s}%s}" % (self.value[1], self.value[0])
                return "{\\frac{{\\delta}^{%s}}{{{\\delta}%s}^{%s}}%s}" % (self.value[2], self.value[1], self.value[2], self.value[0])
            elif self.method is "pow":
                return "{%s^%s}" % self.value
            elif self.method is "neg":
                return "{-%s}" % self.value
            elif self.method is "sigma":
                return "{\\sum_{%s = %s}^{%s}(%s)}" % self.value
            elif self.method is "pi":
                return "{\\prod_{%s = %s}^{%s}(%s)}" % self.value
            elif self.method is "factorial":
                if self.value.is_base or is_float(self.value):
                    return "{%s!}" % self.value
                return "{(%s)!}" % self.value
            else:
                # mains
                if not self.method.startswith("\\") and not self.method in ["=", "<", ">"]:
                    self.method = "\\{}".format(self.method)
                if self.mtype is "binf":
                    return "{%s(%s)}" % (self.method, ", ".join(map(str, self.value)))
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

    def to_latex(self, display_style=True):
        original_mode = exp.mode
        exp.mode = 2
        to_return = self.__repr__()
        exp.mode = original_mode
        if display_style:
            to_return = '\displaystyle' + to_return
        return to_return

    @staticmethod
    def generic_method(inputs, method, **kwargs):
        return exp(_to_exp(inputs), method=method, **kwargs)

    @staticmethod
    def binary(inputs, method, **kwargs):
        """ unless specially defined in __repr__, f(a,b,c,...) notation and f(a,b,c,...) latex """
        return exp.generic_method(inputs, method, mtype="binf", **kwargs)

    @staticmethod
    def mbinary(inputs, method, **kwargs):
        """ a f b notation and a f b latex"""
        return exp.generic_method(inputs, method, mtype="binm", **kwargs)

    @staticmethod
    def sbinary(inputs, method, **kwargs):
        """ a f b notation and f{a}{b} latex"""
        return exp.generic_method(inputs, method, mtype="bins", **kwargs)

    @staticmethod
    def comp(inputs, method, **kwargs):
        """ a comp b notation and a comp b latex"""
        return exp.generic_method(inputs, method, mtype="binr", **kwargs)

    @staticmethod
    def unary(input, method, **kwargs):
        """ unless specially defined in __repr__, f(a) notation and f(a) latex """
        if isinstance(input, tuple):
            input = input[0]
        return exp.generic_method(input, method, mtype="unaf", **kwargs)

    @staticmethod
    def sunary(input, method, **kwargs):
        """ f(a) notation and f{a} latex """
        if isinstance(input, tuple):
            input = input[0]
        return exp.generic_method(input, method, mtype="unas", **kwargs)

    # binary operators
    def __add__(self, other):
        return exp.binary((self, other), method="add", evalf=lambda x, y: x + y)

    def __radd__(self, other):
        return exp(other) + self

    def __mul__(self, other):
        return exp.binary((self, other), method="mul", evalf=lambda x, y: x * y)

    def __rmul__(self, other):
        return exp(other) * self
    
    def __sub__(self, other):
        return exp.binary((self, other), method="sub", evalf=lambda x, y: x - y)

    def __rsub__(self, other):
        return exp(other) - self

    def __truediv__(self, other):
        # not just exp.sbinary(..., "\\frac") because __repr__ should print div(a, b) not \frac(a, b)
        return exp.binary((self, other), method="div", evalf=lambda x, y: x / y)

    def __rtruediv__(self, other):
        return exp(other) / self

    def __pow__(self, power, modulo=None):
        return exp.binary((self, power), method="pow", evalf=lambda x, y: x ** y)

    def __rpow__(self, other):
        return exp(other) ** self

    # unary operators
    def __neg__(self):
        return exp.unary(self, method="neg", evalf=lambda x: -x)

    # comparison operators
    def __eq__(self, other):
        return exp.comp((self, other), method="=", evalf=lambda x, y: x == y)

    def __ne__(self, other):
        return exp.comp((self, other), method="neq", evalf=lambda x, y: x != y)

    def __lt__(self, other):
        return exp.comp((self, other), method="<", evalf=lambda x, y: x < y)

    def __gt__(self, other):
        return exp.comp((self, other), method=">", evalf=lambda x, y: x > y)

    def __le__(self, other):
        return exp.comp((self, other), method="leq", evalf=lambda x, y: x <= y)

    def __ge__(self, other):
        return exp.comp((self, other), method="geq", evalf=lambda x, y: x >= y)

    # binary statics

    # unary statics
    @staticmethod
    def sin(expr):
        return exp.unary(expr, "sin", evalf=lambda x: math.sin(x))

    @staticmethod
    def cos(expr):
        return exp.unary(expr, "cos", evalf=lambda x: math.cos(x))

    @staticmethod
    def tan(expr):
        return exp.unary(expr, "tan", evalf=lambda x: math.tan(x))

    @staticmethod
    def cot(expr):
        return exp.unary(expr, "cot", evalf=lambda x: 1/math.tan(x))

    @staticmethod
    def csc(expr):
        return exp.unary(expr, "csc", evalf=lambda x: 1/math.sin(x))

    @staticmethod
    def sec(expr):
        return exp.unary(expr, "sec", evalf=lambda x: 1/math.cos(x))

    @staticmethod
    def log(expr, base=None):
        if base is None:
            return exp.ln(expr)
        return exp.unary(expr, "log_{%s}" % str(base), evalf=lambda x: math.log(x, base))

    @staticmethod
    def ln(expr):
        return exp.unary(expr, "ln", evalf=lambda x: math.log(x))

    @staticmethod
    def sqrt(expr):
        return exp.sunary(expr, "sqrt", evalf=lambda x: math.sqrt(x))

    @staticmethod
    def deriv(expr_u, expr_v, n=1):
        if not (isinstance(n, int) and n > 0):
            raise ValueError("Cannot take \"{}\"-th derivative".format(n))
        return exp.binary((expr_u, expr_v, n), "nderiv", evalf=deriv_evalf, ignores_vars=True)

    @staticmethod
    def partial(expr_u, expr_v, n=1):
        if not (isinstance(n, int) and n > 0):
            raise ValueError("Cannot take \"{}\"-th derivative".format(n))
        return exp.binary((expr_u, expr_v, n), "npartial", evalf=partial_evalf, ignores_vars=True)

    @staticmethod
    def sigma(vari, fro, to, expr):
        return exp.binary((vari, fro, to, expr), "sigma", evalf=functools.partial(sum_prod_evalf, typef=sum), ignores_vars=True)

    @staticmethod
    def sum(*args):
        return exp.sigma(*args)

    @staticmethod
    def big_pi(vari, fro, to, expr):
        return exp.binary((vari, fro, to, expr), "pi",
                          evalf=functools.partial(sum_prod_evalf, typef=functools.partial(functools.reduce, mul)),
                          ignores_vars=True)

    @staticmethod
    def product(*args):
        return exp.big_pi(*args)

    @staticmethod
    def factorial(expr):
        return exp.sunary(expr, "factorial", evalf=factorial)

    # comparison statics


class text(latex):
    def __init__(self, text):
        if isinstance(text, str):
            self.text = "\\textrm{ %s }" % text
        else:
            TypeError("\"text\" parameter \"{}\" must be str".format(text))

    def to_latex(self):
        return self.text


class line:
    def __init__(self, *exps):
        self.exps = exps

    def add(self, *exps):
        self.exps += exps

    def __repr__(self):
        return " ".join([i.to_latex() for i in self.exps])


class doc:
    def __init__(self, *lines, name=None):
        self.lines = lines
        self.name = name
        if self.name is None:
            self.name = _rand_filename()

    def create(self):
        lines = "\n".join(["$$%s$$" % l for l in self.lines])
        docx = Document(data=NoEscape(lines))
        docx.generate_pdf(self.name)




