from .document import doc, line


class Latexable:
    def __init__(self):
        pass

    def create(self, name=None):
        doc(line(self), name=name).create()

    def to_latex(self):
        """ to be defined in child classes """
        pass
