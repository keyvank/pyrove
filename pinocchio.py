from polynomial import PolynomialP
from fieldp import FieldP
from vector import Vector
from r1cs import CircuitGenerator
from pairing import G1,G2,e

def mul(pols, sol):
    return sum([pols[i] * sol[i] for i in range(len(sol))], PolynomialP([]))

class QAP:
    def __init__(self, circuit):
        consts = len(circuit.L)

         # Toxic waste
        alpha = FieldP(123)
        beta = FieldP(234)
        gamma = FieldP(345)
        delta = FieldP(456)
        tau = FieldP(12345)
        taus = [FieldP(1)]
        for i in range(100):
            taus.append(taus[-1] * tau)

        self.taus = Vector(taus)
        self.L = [PolynomialP.interpolate(l) for l in list(zip(*circuit.L))]
        self.R = [PolynomialP.interpolate(r) for r in list(zip(*circuit.R))]
        self.O = [PolynomialP.interpolate(o) for o in list(zip(*circuit.O))]
        self.Z = PolynomialP.z(consts)
        self.Ltau = Vector([p.evaluate(tau) for p in self.L])
        self.Rtau = Vector([p.evaluate(tau) for p in self.R])
        self.Otau = Vector([p.evaluate(tau) for p in self.O])
        self.Ztau = self.Z.evaluate(tau)

    def prove(self, inputs, solution):
        sol = [FieldP(0)] * len(circuit.symbols)
        for k, v in solution.items():
            sol[circuit.symbols[k]] = v
        for k, v in inputs.items():
            sol[circuit.symbols[k]] = v
        solall = Vector(sol)

        # FFT
        H = Vector(((mul(self.L, solall) * mul(self.R, solall) - mul(self.O, solall)) / self.Z).coefs)

        for k, v in inputs.items():
            sol[circuit.symbols[k]] = FieldP(0)
        solio = Vector(sol)

        Lt = self.Ltau.dot(solio) # Multiexp
        Rt = self.Rtau.dot(solio) # Multiexp
        Ot = self.Otau.dot(solio) # Multiexp
        Ht = H.dot(self.taus) # Multiexp
        Zt = self.Ztau
        return (Lt,Rt,Ot,Ht,Zt)

    def verify(self, inps, proof):
        sol = [FieldP(0)] * len(circuit.symbols)
        for k, v in inps.items():
            sol[circuit.symbols[k]] = v
        sol = Vector(sol)
        Lt,Rt,Ot,Ht,Zt = proof
        Lt += self.Ltau.dot(sol) # Multiexp
        Rt += self.Rtau.dot(sol) # Multiexp
        Ot += self.Otau.dot(sol) # Multiexp
        return (Lt*Rt-Ot- Ht*Zt) == FieldP(0)
        #return (Lt,Rt,Ot,Ht,Zt)
        #Lt,Rt,Ot,Ht,Zt = proof
        #return Lt*Rt-Ot-Ht*Zt


if __name__ == '__main__':
    g = CircuitGenerator()

    g.mul('x^2', 'x', 'x')
    g.mul('x^3', 'x^2', 'x')
    g.add('x^3+x', 'x^3', 'x')
    g.add('x^3+x+6', 'x^3+x', FieldP(6))
    g.mul('(x^3+x+6)^2', 'x^3+x+6', 'x^3+x+6')
    circuit = g.compile()
    qap = QAP(circuit)

    inputs = {'(x^3+x+6)^2': FieldP(1296)}

    solution = {'1': FieldP(1),
                'x': FieldP(3),
                'x^2': FieldP(9),
                'x^3': FieldP(27),
                'x^3+x': FieldP(30),
                'x^3+x+6': FieldP(36)}

    proof = qap.prove(inputs, solution)
    print(qap.verify(inputs, proof))
