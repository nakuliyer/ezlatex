# from pylatex import Document, Section, Subsection, Command, Math, Alignat
# from pylatex.utils import italic, NoEscape
# import string
#
#
# def flatten(l):
#     """
#     Flattens two-dimensional list. Used on commutative methods.
#
#     :param l: (list) - two-dimensional list
#     :return: (list) - one-dimensional list
#     """
#     q = []
#     for sublist in l:
#         if isinstance(sublist, list):
#             for item in sublist:
#                 q.append(item)
#         else:
#             q.append(sublist)
#     return q
#
#
# def strong_flatten(l):
#     """
#     Flattens multidimensional array recursively.
#
#     :param l: (list) - list of any dimension
#     :return: (list) - one-dimensional list
#     """
#
#     q = flatten(l)
#     b = False
#     for sublist in l:
#         if isinstance(sublist, list):
#             b = True
#     if b:
#         return strong_flatten(q)
#     return q
#
#
# def strong_parenthetical(l):
#     """
#     Converts lists to parenthetical notation for printing.
#
#     :param l: (list)
#     :return: (str)
#     """
#     q = "("
#     for i, item in enumerate(l):
#         if isinstance(item, str):
#             q += item
#         elif isinstance(item, list):
#             q += strong_parenthetical(item)
#
#         if not i == len(l) - 1:
#             q += " "
#     q += ")"
#     return q
#
#
# def is_float(expr):
#     if not type(expr.value) == str:
#         return False
#     try:
#         float(expr.value)
#         if expr.method is None:
#             return True
#         return False
#     except ValueError:
#         return False
#
#
# def is_var(expr):
#     l = list(string.ascii_lowercase)
#     if expr.value in l:
#         return True
#     return False
#
# class exp:
#     """ Expressions """
#
#     """ Class Variables """
#     count = 0
#     DEF_VARIABLES = ["x", "y", "z", "w"]  # or x_1, x_2, x_3, notation in the future
#     mode = 1  # 0 for basic, 1 for regular notation, 2 for latex
#
#     def __init__(self, value=None, method=None, base=None):
#         """
#         Initializes Variable
#         """
#         self.method = method
#         self.base = False
#         if isinstance(value, (list, tuple)):
#             self.value = tuple(value)
#         elif isinstance(value, str):
#             self.value = value
#             self.base = True
#         elif isinstance(value, (int, float)):
#             self.value = str(value)
#         elif isinstance(value, exp):
#             self.value = value
#             if self.method is None:
#                 self.method = "pro"  # protected (parenthesis)
#         elif value is None:
#             if exp.count < len(exp.DEF_VARIABLES):
#                 self.value = exp.DEF_VARIABLES[exp.count]
#                 self.base = True
#                 exp.count += 1
#             # TODO: otherwise, return subscripted number
#         if base is not None:
#             self.base = base
#
#     def __repr__(self):
#         if self.method is None:
#             return str(self.value)
#         elif exp.mode == 0:
#             if isinstance(self.value, tuple):
#                 return "%s%s" % (self.method, str(self.value))
#             return "%s(%s)" % (self.method, str(self.value))
#         elif exp.mode == 1:
#             if self.method is "pro":
#                 return "(%s)" % self.value
#             elif self.method is "add":
#                 return "%s + %s" % self.value
#             elif self.method is "sub":
#                 return "%s - %s" % self.value
#             elif self.method is "mul":
#                 if self.value[0].base and not self.value[1].base:
#                     return "%s%s" % tuple(reversed(self.value))
#                 if self.value[1].base:
#                     return "%s%s" % self.value
#                 return "%s(%s)" % self.value
#             elif self.method is "div":
#                 return "%s/%s" % self.value
#             elif self.method is "pow":
#                 return "%s^%s" % self.value
#             elif self.method is "neg":
#                 return "-%s" % self.value
#             elif self.method is "sqrt":
#                 return "sqrt(%s)" % self.value
#             elif self.method[0:4] == "bin:":
#                 return "%s(%s, %s)" % (self.method[5:], self.value[0], self.value[1])
#             elif self.method[0:4] == "mbn:":
#                 return "%s %s %s" % (self.value[0], self.method[5:], self.value[1])
#             elif self.method[0:4] == "uni:":
#                 return "%s(%s)" % (self.method[5:], self.value)
#             raise ValueError("Invalid Function \"{}\"".format(self.method))
#         elif exp.mode == 2:
#             if self.method is "pro":
#                 return "(%s)" % self.value
#             elif self.method is "add":
#                 return "{%s+%s}" % self.value
#             elif self.method is "sub":
#                 return "{%s-%s}" % self.value
#             elif self.method is "mul":
#                 if self.value[0].base and not self.value[1].base:
#                     return "{%s%s}" % tuple(reversed(self.value))
#                 if self.value[1].base:
#                     return "{%s%s}" % self.value
#                 return "{%s(%s)}" % self.value
#             elif self.method is "div":
#                 return "{\\frac{%s}{%s}}" % self.value
#             elif self.method is "pow":
#                 return "{%s^%s}" % self.value
#             elif self.method is "sqrt":
#                 return "{\\sqrt{%s}}" % self.value
#             elif self.method is "neg":
#                 return "{-%s}" % self.value
#             elif self.method[0:4] == "bin:":
#                 start = "\\" if self.method[4] == "f" else ""
#                 return "{%s%s(%s, %s)}" % (start, self.method[5:], self.value[0], self.value[1])
#             elif self.method[0:4] == "mbn:":
#                 start = ""
#                 if self.method[4] == "f":
#                     start = "\\"
#                 elif self.method[4] == "r":
#                     return "%s %s %s" % (self.value[0], self.method[5:], self.value[1])
#                 return "{%s %s%s %s}" % (self.value[0], start, self.method[5:], self.value[1])
#             elif self.method[0:4] == "uni:":
#                 start = "\\" if self.method[4] == "f" else ""
#                 return "{%s%s(%s)}" % (start, self.method[5:], self.value)
#             raise ValueError("Invalid Function \"{}\"".format(self.method))
#         raise ValueError("Mode Unavailable")
#
#     def create(self):
#         original_mode = exp.mode
#         exp.mode = 2
#         doc = Document('basic')
#         with doc.create(Alignat(numbering=False, escape=False)) as agn:
#             agn.append(self.__repr__())
#         doc.generate_pdf()
#         exp.mode = original_mode
#
#     def bin(self, other, method):
#         if isinstance(other, exp):
#             v = other
#         else:
#             v = exp(other)
#         return exp([self, v], method)
#
#     @staticmethod
#     def binary(a, b, method, auto="f"):
#         """ f(a,b) notation """
#         return exp([a, b], "bin:" + auto + method)
#
#     @staticmethod
#     def mbinary(a, b, method, auto="f"):
#         """ (a f b) notation """
#         return exp([a, b], "mbn:" + auto + method)
#
#     @staticmethod
#     def comp(a, b, method, auto="r"):
#         """ (a f b) notation """
#         if auto == "f":
#             method = "\\" + method
#         return exp.mbinary(a, b, method, "r")
#
#     @staticmethod
#     def unary(a, method, auto="f"):
#         return exp(a, "uni:" + auto + method)
#
#     def __add__(self, other):
#         return self.bin(other, "add")
#
#     def __radd__(self, other):
#         return exp(other) + self
#
#     def __mul__(self, other):
#         return self.bin(other, "mul")
#
#     def __rmul__(self, other):
#         return exp(other) * self
#
#     def __sub__(self, other):
#         return self.bin(other, "sub")
#
#     def __rsub__(self, other):
#         return exp(other) - self
#
#     def __truediv__(self, other):
#         return self.bin(other, "div")
#
#     def __rtruediv__(self, other):
#         return exp(other) / self
#
#     def __pow__(self, power, modulo=None):
#         return self.bin(power, "pow")
#
#     def __rpow__(self, other):
#         return exp(other) ** self
#
#     @staticmethod
#     def sin(expr):
#         return exp.unary(expr, "sin")
#
#     @staticmethod
#     def cos(expr):
#         return exp.unary(expr, "cos")
#
#     @staticmethod
#     def tan(expr):
#         return exp.unary(expr, "tan")
#
#     @staticmethod
#     def cot(expr):
#         return exp.unary(expr, "cot")
#
#     @staticmethod
#     def csc(expr):
#         return exp.unary(expr, "csc")
#
#     @staticmethod
#     def sec(expr):
#         return exp.unary(expr, "sec")
#
#     @staticmethod
#     def log(expr):
#         return exp.unary(expr, "log")
#
#     @staticmethod
#     def ln(expr):
#         return exp.unary(expr, "ln")
#
#     @staticmethod
#     def sqrt(expr):
#         return exp(expr, "sqrt")
#
#     def __eq__(self, other):
#         return exp.comp(self, other, "=")
#
#     def __ne__(self, other):
#         return exp.comp(self, other, "neq", "f")
#
#     def __lt__(self, other):
#         return exp.comp(self, other, "<")
#
#     def __gt__(self, other):
#         return exp.comp(self, other, ">")
#
#     def __neg__(self):
#         return exp(self, "neg")
#
