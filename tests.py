from ezlatex import exp, text, doc, line

a = exp('a')
b = exp('b')
c = exp('c')
d = exp('d')

x = (-b - exp.sqrt(b ** 2 - 4 * a * c)) / (2 * a)

print(x(a=1, b=5, c=6))
