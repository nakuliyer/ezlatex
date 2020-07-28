from ezlatex import exp

exp.mode = 2  # See the LaTeX instead of a nicer string

# Creating new variables
a = exp("a")
x_0 = exp()
print(a*x_0)

# Using constants
from ezlatex.consts import a, b, c
print(exp.mbinary((-b, exp.sqrt(b**2-4*a*c)), "\\pm")/(2*a))
print(a**2+b**2 == c**2-2*a*b*exp.cos(c))

from ezlatex.consts import m, n, k
print(a**m+b**n==c**k)

from ezlatex.consts import e, i, pi
print(e**(i*pi) == -1)

from ezlatex.consts import x, y, z
print(exp.deriv(x**2, x) == 2*x)
print(exp.deriv(x**2, x, n=2) == 2)

from ezlatex.consts import hbar, c, pi, G, M, T
print(T == (hbar*c**3)/(8*pi*G*M*exp("k_b")))

from ezlatex.consts import i, hbar, psi, t, m, x, y, z, V
print(i*hbar*exp.deriv(psi, t) == -hbar**2/(2*m)*exp(exp.partial(psi, x, 2)+exp.partial(psi, y, 2)+exp.partial(psi, z, 2))+V*psi)