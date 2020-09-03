from pylatex import Document, Alignat, NoEscape

from .utils import rand_filename


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
            self.name = rand_filename()

    def create(self):
        lines = "\n".join(["$$%s$$" % l for l in self.lines])
        docx = Document(data=NoEscape(lines))
        docx.generate_pdf(self.name)