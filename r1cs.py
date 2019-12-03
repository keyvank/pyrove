from vector import Vector
from fieldp import FieldP
from gadgets.var import Var
from gadgets.gadget import Gadget, Mul, Add

class R1CSCircuit:
    def __init__(self, inputs, L, R, O):
        self.inputs = inputs
        self.L, self.R, self.O = L, R, O

class Gate:
    def __init__(self, l, r, o):
        self.l, self.r, self.o = l, r, o

class CircuitGenerator:

    def __init__(self):
        self.vars = []
        self.inputs = {}
        self.gates = []
        self.one = self.create_var(FieldP(1))
        self.create_input(self.one, '1')

    def create_input(self, v, name):
        if name not in self.inputs:
            self.vars.remove(v)
            self.vars.insert(len(self.inputs), v)
            self.inputs[name] = v
        else:
            raise Exception("Input already exist!")

    def create_var(self, value = None):
        v = Var()
        self.vars.append(v)
        if value:
            v.assign(value)
        return v

    def constrain(self, a, b, c):
        self.gates.append(Gate(a, b, c))

    def _check(self):
        # Check if all variables are assigned
        for v in self.vars:
            if not v.is_assigned():
                raise Exception("Not all variables are assigned!")

        # Check if all values satisfy the gates
        for g in self.gates:
            L = sum([v.value * coef for v, coef in g.l.items()], FieldP(0))
            R = sum([v.value * coef for v, coef in g.r.items()], FieldP(0))
            O = sum([v.value * coef for v, coef in g.o.items()], FieldP(0))
            res = L * R - O
            if res != FieldP(0):
                raise Exception("Gates not satisfied!")

    def sol(self):
        self._check()
        return Vector([v.value for v in self.vars])

    def inp(self):
        self._check()
        return Vector([v.value for i, v in enumerate(self.vars) if i < len(self.inputs)])

    def compile(self):
        syms = {sym: i for i, sym in enumerate(self.vars)}
        LRO = [[[FieldP(0)] * len(syms) for i in range(len(self.gates))]
               for i in range(3)]
        for i, gate in enumerate(self.gates):
            for k, v in gate.l.items():
                LRO[0][i][syms[k]] = v
            LRO[0][i] = Vector(LRO[0][i])
            for k, v in gate.r.items():
                LRO[1][i][syms[k]] = v
            LRO[1][i] = Vector(LRO[1][i])
            for k, v in gate.o.items():
                LRO[2][i][syms[k]] = v
            LRO[2][i] = Vector(LRO[2][i])
        return R1CSCircuit(list(self.inputs.keys()), LRO[0], LRO[1], LRO[2])
