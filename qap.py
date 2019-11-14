from polynomial import PolynomialP

class QAP:
    def __init__(self, circuit):
        self.num_publics = circuit.num_publics
        self.L = [PolynomialP.interpolate(l) for l in list(zip(*circuit.L))]
        self.R = [PolynomialP.interpolate(r) for r in list(zip(*circuit.R))]
        self.O = [PolynomialP.interpolate(o) for o in list(zip(*circuit.O))]
        self.Z = PolynomialP.z(len(circuit.L))
