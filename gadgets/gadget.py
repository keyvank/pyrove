from .var import Var
from fieldp import FieldP

class Gadget:
    def __init__(self, circuit, deps):
        self.circuit = circuit
        self.deps = set()
        for v in deps:
            if not v.is_assigned():
                self.deps.add(v)
                v.depend(self.callback)
        if not self.deps:
            self.evaluate()

    def callback(self, v):
        self.deps.remove(v)
        if not self.deps:
            self.evaluate()

    def evaluate(self):
        pass

class Mul(Gadget):
    def __init__(self, circuit, a, b):
        self.a = a
        self.b = b
        self.c = circuit.create_var()
        circuit.constrain({self.a: FieldP(1)}, {self.b: FieldP(1)}, {self.c: FieldP(1)})
        super().__init__(circuit, {a, b})

    def output(self):
        return self.c

    def evaluate(self):
        self.c.assign(self.a.value * self.b.value)

class Add(Gadget):
    def __init__(self, circuit, a, b):
        self.a = a
        self.b = b
        self.c = circuit.create_var()
        circuit.constrain({self.a: FieldP(1), self.b: FieldP(1)}, {circuit.one: FieldP(1)}, {self.c: FieldP(1)})
        super().__init__(circuit, {a, b})

    def output(self):
        return self.c

    def evaluate(self):
        self.c.assign(self.a.value + self.b.value)
