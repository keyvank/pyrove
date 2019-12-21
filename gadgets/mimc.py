from .gadget import Gadget, Mul, Add
from fieldp import FieldP

class MiMC(Gadget):
    def __init__(self, circuit, a):
        self.a = a
        curr = self.a
        for r in range(4):
            curr2 = Mul(circuit, curr, curr).output()
            curr3 = Mul(circuit, curr2, curr).output()
            curr = Add(circuit, curr3, circuit.create_var(FieldP(r))).output()
        self.o = curr
        super().__init__(circuit, {self.a,})

    def output(self):
        return self.o

    def evaluate(self):
        v = self.a.value
        for r in range(4):
            v = v * v * v + FieldP(r)
        self.o.assign(v)
