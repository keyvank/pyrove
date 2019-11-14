from polynomial import PolynomialP
from fieldp import FieldP
from vector import Vector
from r1cs import CircuitGenerator
from qap import QAP
from pairing import G1,G2,e

def mul(pols, sol):
    return sum([pols[i] * sol[i] for i in range(len(sol))], PolynomialP([]))

class Pinocchio:
    def __init__(self, qap):
        self.qap = qap

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
        self.Ltau = Vector([p.evaluate(tau) for p in self.qap.L])
        self.Rtau = Vector([p.evaluate(tau) for p in self.qap.R])
        self.Otau = Vector([p.evaluate(tau) for p in self.qap.O])
        self.Ztau = self.qap.Z.evaluate(tau)

    def prove(self, inputs, solution):
        sol = [FieldP(0)] * len(circuit.symbols)
        for k, v in solution.items():
            sol[circuit.symbols[k]] = v
        for k, v in inputs.items():
            sol[circuit.symbols[k]] = v
        solall = Vector(sol)

        # FFT
        H = Vector(((mul(self.qap.L, solall) * mul(self.qap.R, solall) - mul(self.qap.O, solall)) / self.qap.Z).coefs)

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
    pino = Pinocchio(qap)

    inputs = {'(x^3+x+6)^2': FieldP(1296)}

    solution = {'1': FieldP(1),
                'x': FieldP(3),
                'x^2': FieldP(9),
                'x^3': FieldP(27),
                'x^3+x': FieldP(30),
                'x^3+x+6': FieldP(36)}

    proof = pino.prove(inputs, solution)
    print(pino.verify(inputs, proof))
