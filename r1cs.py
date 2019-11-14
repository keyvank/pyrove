from vector import Vector
from fieldp import FieldP

class R1CSCircuit:

    def __init__(self, symbols, num_publics, L, R, O):
        self.symbols = symbols
        self.num_publics = num_publics
        self.L, self.R, self.O = L, R, O

    def verify(self, solution):
        sol = [FieldP(0)] * len(self.symbols)
        for k, v in solution.items():
            sol[self.symbols[k]] = v
        sol = Vector(sol)
        L = Vector((v.dot(sol) for v in self.L))
        R = Vector((v.dot(sol) for v in self.R))
        O = Vector((v.dot(sol) for v in self.O))
        result = L * R - O
        return result.dot(result) == FieldP(0)

class CircuitGenerator:

    def __init__(self):
        self.gates = []
        self.vars = set()

    def _new_var(self, var):
        if var in self.vars:
            raise Exception("'{}' is already set!".format(var))
        self.vars.add(var)

    def mov(self, result, a):
        l = {'1': a} if type(a) is FieldP else {a: FieldP(1)}
        r = {'1': FieldP(1)}
        o = {result: FieldP(1)}
        self._new_var(result)
        self.gates.append((l, r, o))

    def mul(self, result, a, b):
        l = {'1': a} if type(a) is FieldP else {a: FieldP(1)}
        r = {'1': b} if type(b) is FieldP else {b: FieldP(1)}
        o = {result: FieldP(1)}
        self._new_var(result)
        self.gates.append((l, r, o))

    def neg(self, result, a):
        self.mul(result, '-1', a)

    def add(self, result, a, b):
        if type(a) is FieldP and type(b) is FieldP:
            self.mov(result, a + b)
            return
        if a == b:
            self.mul(result, a, FieldP(2))
            return
        l = {'1': a} if type(a) is FieldP else {a: FieldP(1)}
        l.update({'1': b} if type(b) is FieldP else {b: FieldP(1)})
        r = {'1': FieldP(1)}
        o = {result: FieldP(1)}
        self._new_var(result)
        self.gates.append((l,r,o))

    def compile(self, inputs):
        syms = set()
        for gate in self.gates:
            for part in gate:
                syms.update(part.keys())
        if not inputs.issubset(syms):
            raise Error("Invalid inputs!")
        syms.difference_update(inputs)
        syms = {sym: i for i,sym in enumerate(list(inputs) + list(syms))}
        LRO = [[[FieldP(0)] * len(syms) for i in range(len(self.gates))] for i in range(3)]
        for i, gate in enumerate(self.gates):
            for j in range(3):
                for k,v in gate[j].items():
                    LRO[j][i][syms[k]] = v
                LRO[j][i] = Vector(LRO[j][i])
        return R1CSCircuit(syms, len(inputs), LRO[0], LRO[1], LRO[2])
