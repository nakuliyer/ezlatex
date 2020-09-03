from ezlatex import exp, expression, text, doc, line
from ezlatex.consts import hbar, psi, m, t, i, x, y, z, V, a, b, c, k
import math
# q = exp.big_pi("i", 1, exp("n"), exp("v")*exp("i"))
# print(q)
# print(q.to_latex())
# print(q(v=1, n=5))
# # q.create()

@expression
def f(a, b, c):
    return a**2 + 45 * b / c

# f = schrodinger = i*hbar*exp.partial(psi, t) == -hbar**2/(2*m)*exp(exp.partial(psi, x, 2)+exp.partial(psi, y, 2)+exp.partial(psi, z, 2))+V*psi

# print(f.to_latex())
print(f(1, -4, 6))

f = exp.indef_integral(x, x**2)
print(f.to_latex())

exp._mode = 2
x = exp("x")
n = exp("n")
# q = exp.sin(x) == exp.sigma(n, 0, infty, exp(-1)**n / exp.factorial(2*n+1) * x**(2*n+1))
# q = exp.deriv(x**2, x)
# exp.mode = 2
# q = exp.deriv((x ** 5)**2, x)
# q = exp.nroot(x, 3)
q = exp.integral(x, 1, 2, exp.sin(x))
print(q)
# print(q())

# x = exp("x")
# q = exp(exp.sin(x) + exp("r") * x + x**2 + exp("f") * exp() ** x)
# print(q(r=2, x_0=5, x=1)(f=1))
# exp.mode = 2
# x = exp("x")
# q = exp.deriv(exp("x") * 2, x, 1)
# # q = exp(9) * 8 * 84
# print(q)

# q = exp.sin(exp("x"))
# print(q(x=5))
# print(q)
# q = exp.sin(exp.log(exp("x"), 2))
# q = exp("x") ** 2 == 15 - exp.sqrt(36)
# print(q)
# print(q(x=3))
#
# exp.mode = 2  # See the LaTeX instead of a nicer string
#
# # Creating new variables
# a = exp("a")
# x_0 = exp()
# print(a*x_0)
#
# # Using constants
# from ezlatex.consts import a, b, c
# print(exp.mbinary((-b, exp.sqrt(b**2-4*a*c)), "\\pm")/(2*a))
# print(a**2+b**2 == c**2-2*a*b*exp.cos(c))
#
# from ezlatex.consts import m, n, k
# print(a**m+b**n==c**k)
#
# from ezlatex.consts import e, i, pi
# print(e**(i*pi) == -1)
#
# from ezlatex.consts import x
# print(exp.deriv(x**2, x) == 2*x)
# print(exp.deriv(x**2, x, n=2) == 2)
# ev = exp.deriv(x**2, x, n=2)
# # ev()
#
# from ezlatex.consts import hbar, c, pi, G, M, T
# print(T == (hbar*c**3)/(8*pi*G*M*exp("k_b")))
#
# from ezlatex.consts import i, hbar, psi, t, m, x, y, z, V
# schrodinger = i*hbar*exp.partial(psi, t) == -hbar**2/(2*m)*exp(exp.partial(psi, x, 2)+exp.partial(psi, y, 2)+exp.partial(psi, z, 2))+V*psi
# exp.mode = 1
# print(schrodinger)
# exp.mode = 2
# print("A")
# # schrodinger.create()
#
# from ezlatex.consts import delta
# print(delta * x)
# print(exp.sqrt(delta))
#
# pythag = a**2+b**2==c**2
# fermat = a**m+b**n==c**k
# docx = doc(line(text("In the year $-1$ million, pythagoras proved that "), pythag, text("was true")), line(text("But, "), fermat, text("Might not be")), name="logic")
# docx.create()
#
# q = a + b
# exp.mode = 0
# print(q)
# exp.mode = 1
# print(q)
# exp.mode = 2
# print(q)