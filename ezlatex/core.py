import functools
import math
import inspect
from operator import mul

from .latexable import Latexable
from .utils import to_float


def to_exp(items):
    """ Converts items to exp. If items is a list, then each item will be converted; if otherwise, items itself will be.

    Args:
        items: A `str`, `int`, `float`, `list`, `tuple` or `exp` to be converted to an `exp`

    Returns:
        exp: converted items
    """
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


def simple(f):
    """ Wrapper for simple functions that require all inputs to be computed before the function can proceed. """
    def get_values(*args, **kwargs):
        values = []
        for i in range(len(args)):
            values.append(args[i](**kwargs))
        try:
            return f(*values)
        except TypeError:
            return None
    return get_values


# def expression(f):
#     """ Wrapper for functions to use that converts all inputs into expressions, with special features:
#
#         .. code-block:: python
#
#             >>> @expression
#             >>> def f(a, b, c):
#             >>>    return a**2 + 45 * b / c
#             >>> f()  # this is an expression
#             a^2 + 45b / c
#             >>> f(1, -5, 6)  # this is a float
#             -29.0
#             >>> f(a=1, b=2)  # this is an expression
#             1 + 90 / c
#         """
#     def expressionify(*args, **kwargs):
#         arg_names = inspect.getfullargspec(f).args
#         if len(kwargs) > 0:
#             return f(*[exp(arg) for arg in arg_names])(**kwargs)
#         if len(args) < len(arg_names):
#             return f(*[exp(arg) for arg in arg_names])
#         new_kwargs = {}
#         for arg_idx in range(len(arg_names)):
#             new_kwargs[arg_names[arg_idx]] = args[arg_idx]
#         return f(*[exp(arg) for arg in arg_names])(**new_kwargs)
#     return expressionify


# def latexify(f):
#     """ Wrapper for functions to use that converts all inputs into latex, with special features:
#
#         .. code-block:: python
#
#             >>> @latexify
#             >>> def f(a, b, c):
#             >>>    return a**2 + 45 * b / c
#             >>> f()  # this is an expression
#             \displaystyle{{a^2} + {\frac{{45b}}{c}}}
#             >>> f(1, -5, 6)  # this is a float
#             -36.5
#             >>> f(a=1, b=2)  # this is an expression
#             \displaystyle{1 + {\frac{90}{c}}}
#         """
#     def expressionify(*args, **kwargs):
#         arg_names = inspect.getfullargspec(f).args
#         if len(kwargs) > 0:
#             typ = f(*[exp(arg) for arg in arg_names])(**kwargs)
#             if isinstance(typ, exp):
#                 return typ.to_latex()
#             return typ
#         if len(args) < len(arg_names):
#             return f(*[exp(arg) for arg in arg_names]).to_latex()
#         new_kwargs = {}
#         for arg_idx in range(len(arg_names)):
#             new_kwargs[arg_names[arg_idx]] = args[arg_idx]
#         typ = f(*[exp(arg) for arg in arg_names])(**new_kwargs)
#         if isinstance(typ, exp):
#             return typ.to_latex()
#         return typ
#     return expressionify


class exp(Latexable):
    """ LaTeX-able and Callable Expressions. """
    _mode = 1
    _internal_count = 0

    def __init__(self, value=None, method=None, displayf=None, latexf=None, evalf=None, **kwargs):
        """ Initializes an expression.

        Args:
            value: any of the arguments normally passed to this method

                * if type is ``ezlatex.exp`` then this object acts as parenthesis
                * if type is ``str`` then this object is a variable
                * if type is a number then this object is a number
                * if type is a tuple then a method should be passed to evaluate/display
                * if value is ``None`` then this object is a new variable ``x_n``, where ``n`` keeps increasing as we make more
            method (str): method name (i.e. ``"sum"``)
            displayf (func): simple display function
            latexf (func): latex display function
            evalf (func): evaluation function

        Keyword Args:
            override_name (str): override name to be referred to in ``__call__``'s kwargs; also overrides default name creating (i.e. \delta -> delta)
            override_value: override constant value to be used in ``__call__`` (useful for values like infinity, which can be computed as a large real number)
        """

        self.method = method
        self.displayf = displayf
        self.latexf = latexf
        self.evalf = evalf
        self.is_base = False
        self.best_name = None
        self.override_value = kwargs["override_value"] if "override_value" in kwargs else None
        self.override_name = kwargs["override_name"] if "override_name" in kwargs else None

        if value is None:
            value = "x_{}".format(exp._internal_count)
            exp._internal_count += 1

        if isinstance(value, tuple):
            self.value = value
            if self.method is not None:
                res = []
                for item in value:
                    if isinstance(item, exp):
                        res.append(item)
                    else:
                        res.append(exp(item))
                self.value = tuple(res)
        if isinstance(value, list):
            self.value = tuple(value)
            if self.method is not None:
                res = []
                for item in value:
                    if isinstance(item, exp):
                        res.append(item)
                    else:
                        res.append(exp(item))
                self.value = tuple(res)
        if isinstance(value, str):
            converted_float = to_float(value)
            if converted_float is not None:
                value = converted_float  # see next "if" statement for float condition
            else:
                self.is_base = True
                self.value = value
                self.best_name = kwargs["override_name"] if "override_name" in kwargs else value
                if self.value[0] == "\\":
                    # callable by ``delta`` instead of ``\delta``
                    if self.displayf is None:
                        self.displayf = lambda value: value[1:]
                    if self.override_name is None:
                        self.best_name = self.value[1:]
                if self.method is not None:
                    self.value = exp(self.value)
        if isinstance(value, (int, float)):
            self.is_base = False
            self.value = float(value)
            if self.value < 0:
                self.value = -self.value
                self.method = "pro"
                self.displayf = lambda value: "(%s)" % value
                self.latexf = lambda value: "(%s)" % value
                self.evalf = lambda *args, **kwargs: self.value(*args, **kwargs)
            if self.method is not None:
                self.value = exp(self.value)
        if isinstance(value, exp):
            self.value = value
            if self.method is None:
                self.method = "pro"  # parenthesis
                self.displayf = lambda value: "(%s)" % value
                self.latexf = lambda value: "(%s)" % value
                self.evalf = lambda *args, **kwargs: self.value(*args, **kwargs)

        if self.value is None:
            raise TypeError("\"value\" keyword argument not in types [tuple, list, str, int, float, exp]")

    def __call__(self, *args, **kwargs):
        """
        Evaluates all the functions recursively, using kwargs as variables if provided. If not all variables are pro-
        vided, it will evaluate as much as possible into the returned expression.

        .. code-block:: python

            >>> expr = exp.sin("x") + exp("r") * 3
            >>> expr(r=2)
            sin(x) + 6.0                # this is an exp
            >>> exp(x=math.pi, r=2)
            7.0                         # this is a float

        If ``override_value`` `kwarg` is provided in the constructor, that number will override the default value (i.e. a
        display as `\\\\infty`, but a value of `99`).

        If ``override_name`` `kwarg` is provided in the constructor, that name will be used to match the variable in this
        method's `**kwargs`.

        If `evalf` is not provided in the constructor, this will throw a `NotImplementedError`.

        Args:
            *args: none expected
            **kwargs: variables to be computed with

        Returns:
            `float` or `exp`: float if all variables given, else exp
        """
        if self.method is None:
            # variable or number
            if self.override_value is not None:
                return self.override_value
            if isinstance(self.value, float):
                return self.value
            if self.best_name in kwargs:
                return kwargs[self.best_name]
            if not isinstance(self.value, exp):
                return exp(self.value)
            return exp
        if self.evalf is not None:
            # evaluate
            if isinstance(self.value, (list, tuple)):
                return self.evalf(*self.value, **kwargs)
            return self.evalf(self.value, **kwargs)

        raise NotImplementedError("Cannot evaluate \"{}\"".format(self.method))

    def __repr__(self):
        """ Represent an expression. If ``exp._mode`` is:
            * `0`, then this will be a basic representation: a stringified number, variable name, or string of the
            format `[method](first_input, second_input, ....)`.
            * `1`, then this will be a display representation: it will return ``displayf`` if it exists, otherwise the
            same as the basic representation
            * `2`, then this will be a LaTeX representation: it will return ``latexf`` if it exists, otherwise the same
            as the display representation
            """

        if self.method is None:
            if isinstance(self.value, float) and self.value.is_integer():
                return str(int(self.value))
            return str(self.value)
        elif exp._mode == 0:
            if isinstance(self.value, tuple):
                return "%s%s" % (self.method, str(self.value))
            return "%s(%s)" % (self.method, str(self.value))
        elif exp._mode == 1:
            if self.displayf is not None:
                return self.displayf(self.value)
            if isinstance(self.value, tuple):
                return "%s%s" % (self.method, str(self.value))
            return "%s(%s)" % (self.method, str(self.value))
        elif exp._mode == 2:
            if self.latexf is not None:
                return self.latexf(self.value)
            if self.displayf is not None:
                return "{%s}" % self.displayf(self.value)
            if isinstance(self.value, tuple):
                return "%s%s" % (self.method, str(self.value))
            return "%s(%s)" % (self.method, str(self.value))

    def to_latex(self, display_style=True):
        """ Convert to LaTeX. """
        original_mode = exp._mode
        exp._mode = 2
        to_return = self.__repr__()
        exp._mode = original_mode
        if display_style:
            to_return = '\displaystyle' + to_return
        return to_return

    # binary operators
    def __add__(self, other):
        """ Return new expression defined as ``self + other`` """
        def displayf(value): return "%s + %s" % value

        @simple
        def evalf(x, y): return x + y

        return exp((self, other), "sum", displayf=displayf, evalf=evalf)

    def __radd__(self, other):
        return exp(other) + self

    def __mul__(self, other):
        """ Return new expression defined as ``self * other`` """
        def displayf(value):
            if value[0].is_base and not value[1].is_base:
                return "%s%s" % tuple(reversed(value))
            if value[1].is_base:
                return "%s%s" % value
            return "%s(%s)" % value

        @simple
        def evalf(x, y): return x * y

        return exp((self, other), "prod", displayf=displayf, evalf=evalf)

    def __rmul__(self, other):
        return exp(other) * self

    def __sub__(self, other):
        """ Return new expression defined as ``self - other`` """
        def displayf(value): return "%s - %s" % value

        @simple
        def evalf(x, y): return x - y

        return exp((self, other), "diff", displayf=displayf, evalf=evalf)

    def __rsub__(self, other):
        return exp(other) - self

    def __truediv__(self, other):
        """ Return new expression defined as ``self / other``. Displays a fraction in LaTeX. """
        def displayf(value): return "%s / %s" % value

        def latexf(value): return "{\\frac{%s}{%s}}" % value

        @simple
        def evalf(x, y): return x / y

        return exp((self, other), "div", displayf=displayf, latexf=latexf, evalf=evalf)

    def __rtruediv__(self, other):
        return exp(other) / self

    def __pow__(self, power, modulo=None):
        """ Return new expression defined as ``self ^ other`` """
        def displayf(value): return "%s^%s" % value

        def latexf(value):
            if to_float(value[1].value) == 1:
                return "{%s}" % value[0]
            return "{%s^%s}" % value

        @simple
        def evalf(x, y): return x ** y

        return exp((self, power), "pow", displayf=displayf, latexf=latexf, evalf=evalf)

    def __rpow__(self, other):
        return exp(other) ** self

    # unary operators
    def __neg__(self):
        """ Return new expression defined as ``-self`` """
        def displayf(value): return "-%s" % value

        @simple
        def evalf(x): return -x

        return exp(self, "neg", displayf=displayf, evalf=evalf)

    # comparison operators
    def __eq__(self, other):
        """ Return new expression defined as ``self = other`` """
        def displayf(value): return "%s = %s" % value

        @simple
        def evalf(x, y): return x == y

        return exp((self, other), "eq", displayf=displayf, evalf=evalf)

    def __ne__(self, other):
        """ Return new expression defined as ``self \\neq other`` """
        def displayf(value): return "%s != %s" % value

        def latexf(value): return "%s \\neq %s" % value

        @simple
        def evalf(x, y): return x != y

        return exp((self, other), "neq", displayf=displayf, latexf=latexf, evalf=evalf)

    def __lt__(self, other):
        """ Return new expression defined as ``self < other`` """
        def displayf(value): return "%s < %s" % value

        @simple
        def evalf(x, y): return x < y

        return exp((self, other), "less", displayf=displayf, evalf=evalf)

    def __gt__(self, other):
        """ Return new expression defined as ``self > other`` """
        def displayf(value): return "%s > %s" % value

        @simple
        def evalf(x, y): return x > y

        return exp((self, other), "greater", displayf=displayf, evalf=evalf)

    def __le__(self, other):
        """ Return new expression defined as ``self \\leq other`` """
        def displayf(value): return "%s <= %s" % value

        def latexf(value): return "%s \\leq %s" % value

        @simple
        def evalf(x, y): return x <= y

        return exp((self, other), "leq", displayf=displayf, latexf=latexf, evalf=evalf)

    def __ge__(self, other):
        """ Return new expression defined as ``self \\geq other`` """
        def displayf(value): return "%s >= %s" % value

        def latexf(value): return "%s \\geq %s" % value

        @simple
        def evalf(x, y): return x >= y

        return exp((self, other), "geq", displayf=displayf, latexf=latexf, evalf=evalf)

    # binary statics

    # unary statics
    @staticmethod
    def sin(expr):
        """ Return new expression defined as ``sin(expr)`` """
        def latexf(value): return "\\sin(%s)" % value

        @simple
        def evalf(x): return math.sin(x)

        return exp(expr, "sin", latexf=latexf, evalf=evalf)

    @staticmethod
    def cos(expr):
        """ Return new expression defined as ``cos(expr)`` """
        def latexf(value): return "\\cos(%s)" % value

        @simple
        def evalf(x): return math.cos(x)

        return exp(expr, "cos", latexf=latexf, evalf=evalf)

    @staticmethod
    def tan(expr):
        """ Return new expression defined as ``tan(expr)`` """
        def latexf(value): return "\\tan(%s)" % value

        @simple
        def evalf(x): return math.tan(x)

        return exp(expr, "tan", latexf=latexf, evalf=evalf)

    @staticmethod
    def cot(expr):
        """ Return new expression defined as ``cot(expr)`` """
        def latexf(value): return "\\cot(%s)" % value

        @simple
        def evalf(x): return 1 / math.tan(x)

        return exp(expr, "cot", latexf=latexf, evalf=evalf)

    @staticmethod
    def csc(expr):
        """ Return new expression defined as ``csc(expr)`` """
        def latexf(value): return "\\csc(%s)" % value

        @simple
        def evalf(x): return 1 / math.sin(x)

        return exp(expr, "csc", latexf=latexf, evalf=evalf)

    @staticmethod
    def sec(expr):
        """ Return new expression defined as ``sec(expr)`` """
        def latexf(value): return "\\sec(%s)" % value

        @simple
        def evalf(x): return 1 / math.cos(x)

        return exp(expr, "sec", latexf=latexf, evalf=evalf)

    @staticmethod
    def log(expr, base=None):
        """ Return new expression defined as ``log_(base) (expr)`` """
        if base is None:
            return exp.ln(expr)

        def latexf(value): return "{\\log_{%s}(%s)}" % value

        @simple
        def evalf(base, x): return math.log(x, base)

        return exp((base, expr), "log", latexf=latexf, evalf=evalf)

    @staticmethod
    def ln(expr):
        """ Return new expression defined as ``ln(expr)`` """
        def latexf(value): return "{\\ln(%s)}" % value

        @simple
        def evalf(x): return math.log(x)

        return exp(expr, "ln", latexf=latexf, evalf=evalf)

    @staticmethod
    def nroot(expr, root):
        """ Return new expression defined as ``root v/(expr)`` """
        def latexf(value): return "{\\sqrt[%s]{%s}}" % value

        @simple
        def evalf(root, x): return x ** 1/(root)

        return exp((root, expr), "nroot", latexf=latexf, evalf=evalf)

    @staticmethod
    def sqrt(expr):
        def latexf(value): return "{\\sqrt(%s)}" % value

        @simple
        def evalf(x): return math.sqrt(x)

        return exp(expr, "sqrt", latexf=latexf, evalf=evalf)

    @staticmethod
    def deriv(expr_u, expr_v, n=1):
        if not (isinstance(n, int) and n > 0):
            raise ValueError("Cannot take \"{}\"-th derivative".format(n))
        
        def latexf(value):
            if value[0].is_base:
                if int(value[2].value) == 1:
                    print("!")
                    return "{\\frac{\\textrm{d}%s}{\\textrm{d}%s}}" % (value[0], value[1])
                return "{\\frac{\\textrm{d}^{%s}%s}{{\\textrm{d}%s}^{%s}}}" % (
                    value[2], value[0], value[1], value[2])
            if int(value[2].value) == 1:
                return "{\\frac{\\textrm{d}}{\\textrm{d}%s}(%s)}" % (value[1], value[0])
            return "{\\frac{\\textrm{d}^{%s}}{{\\textrm{d}%s}^{%s}}(%s)}" % (
                value[2], value[1], value[2], value[0])
        
        return exp((expr_u, expr_v, n), "nderiv", latexf=latexf)

    @staticmethod
    def deriv(expr_u, expr_v, n):
        return exp.deriv(expr_u, expr_v, n)

    @staticmethod
    def partial(expr_u, expr_v, n=1):
        if not (isinstance(n, int) and n > 0):
            raise ValueError("Cannot take \"{}\"-th derivative".format(n))
        
        def latexf(value):
            if value[0].is_base:
                if value[2].value == 1:
                    return "{\\frac{{\\delta}%s}{{\\delta}%s}}" % (value[0], value[1])
                return "{\\frac{{\\delta}^{%s}%s}{{{\\delta}%s}^{%s}}}" % (
                    value[2], value[0], value[1], value[2])
            if value[2].value == 1:
                return "{\\frac{{\\delta}}{{\\delta}%s}%s}" % (value[1], value[0])
            return "{\\frac{{\\delta}^{%s}}{{{\\delta}%s}^{%s}}%s}" % (
                value[2], value[1], value[2], value[0])

        return exp((expr_u, expr_v, n), "npartial", latexf=latexf)

    @staticmethod
    def npartial(expr_u, expr_v, n):
        return exp.partial(expr_u, expr_v, n)

    @staticmethod
    def sigma(vari, fro, to, expr):
        def latexf(value): return "{\\sum_{%s = %s}^{%s}(%s)}" % value

        def evalf(vari, fro, to, expr, **kwargs):
            if vari.best_name in kwargs:
                raise TypeError("Cannot calculate sum with kwarg \"{}\" passed".format(vari.best_name))
            if isinstance(fro, exp):
                fro = fro(**kwargs)
            if isinstance(to, exp):
                to = to(**kwargs)
            if isinstance(fro, float) and isinstance(to, float):
                l = []
                for i in range(int(fro), int(to) + 1, 1):
                    kwargs[vari.best_name] = i
                    l.append(expr(**kwargs))
                return sum(l)
            raise TypeError("Cannot calculate sum/product from {} to {}".format(fro, to))

        return exp((vari, fro, to, expr), "sigma", latexf=latexf, evalf=evalf)

    @staticmethod
    def big_pi(vari, fro, to, expr):
        def latexf(value): return "{\\prod_{%s = %s}^{%s}(%s)}" % value

        def evalf(vari, fro, to, expr, **kwargs):
            if vari.best_name in kwargs:
                raise TypeError("Cannot calculate sum with kwarg \"{}\" passed".format(vari.best_name))
            if isinstance(fro, exp):
                fro = fro(**kwargs)
            if isinstance(to, exp):
                to = to(**kwargs)
            if isinstance(fro, float) and isinstance(to, float):
                l = []
                for i in range(int(fro), int(to) + 1, 1):
                    kwargs[vari.best_name] = i
                    l.append(expr(**kwargs))
                return functools.reduce(mul, l)
            raise TypeError("Cannot calculate sum/product from {} to {}".format(fro, to))

        return exp((vari, fro, to, expr), "sigma", latexf=latexf, evalf=evalf)

    @staticmethod
    def factorial(expr):
        def displayf(value): return "(%s!)" % value

        def latexf(value):
            if value.is_base or isinstance(value.value, float):
                return "{%s!}" % value
            return "{(%s)!}" % value

        @simple
        def evalf(x): return math.factorial(x)

        return exp(expr, "factorial", displayf=displayf, latexf=latexf, evalf=evalf)

    @staticmethod
    def integral(vari, fro, to, expr):
        def latexf(value): return "{\\int_{%s}^{%s}(%s)\\textrm{d}%s}" % (value[1], value[2], value[3], value[0])

        return exp((vari, fro, to, expr), method="integral", latexf=latexf)

    @staticmethod
    def indef_integral(vari, expr):
        def latexf(value): return "{\\int(%s)\\textrm{d}%s}" % (value[1], value[0])

        return exp((vari, expr), method="indef_integral", latexf=latexf)


class text(Latexable):
    def __init__(self, text):
        if isinstance(text, str):
            self.text = "\\textrm{ %s }" % text
        else:
            TypeError("\"text\" parameter \"{}\" must be str".format(text))

    def to_latex(self):
        return self.text