from polynomial import PolynomialP
from fieldp import FieldP
from vector import Vector
from r1cs import CircuitGenerator
from qap import QAP
from pairing import G1,G2,e

def mul(pols, sol):
    return sum([pols[i] * sol[i] for i in range(len(sol))], PolynomialP([]))

class ProvingKey:
    def __init__(self,
                    gl_Ltau, gr_Rtau, go_Otau,
                    gl_alphalLtau, gr_alpharRtau, go_alphaoOtau,
                    g_taus, glro_betaLROtau):
        self.gl_Ltau = gl_Ltau
        self.gr_Rtau = gr_Rtau
        self.go_Otau = go_Otau
        self.gl_alphalLtau = gl_alphalLtau
        self.gr_alpharRtau = gr_alpharRtau
        self.go_alphaoOtau = go_alphaoOtau
        self.g_taus = g_taus
        self.glro_betaLROtau = glro_betaLROtau

class VerificationKey:
    def __init__(self,
                    g, g_alphal, g_alphar, g_alphao,
                    g_gamma, g_betagamma,
                    gl_Ltau, gr_Rtau, go_Otau, go_Ztau):
        self.g = g
        self.g_alphal = g_alphal
        self.g_alphar = g_alphar
        self.g_alphao = g_alphao
        self.g_gamma = g_gamma
        self.g_betagamma = g_betagamma
        self.gl_Ltau = gl_Ltau
        self.gr_Rtau = gr_Rtau
        self.go_Otau = go_Otau
        self.go_Ztau = go_Ztau

class Pinocchio:
    def __init__(self, qap):
        self.qap = qap

        # Toxic waste
        r_l = FieldP(123)
        r_r = FieldP(234)
        alphal = FieldP(345)
        alphar = FieldP(456)
        alphao = FieldP(789)
        beta = FieldP(8910)
        gamma = FieldP(910111)
        tau = FieldP(101112)

        g = G1()
        g_l = G1() * r_l
        g_r = G1() * r_r
        g_o = G1() * (r_l * r_r)

        # Proving key
        pk = ProvingKey(gl_Ltau = Vector([g_l * p.evaluate(tau) for p in self.qap.L[self.qap.num_publics:]]),
                        gr_Rtau = Vector([g_r * p.evaluate(tau) for p in self.qap.R[self.qap.num_publics:]]),
                        go_Otau = Vector([g_o * p.evaluate(tau) for p in self.qap.O[self.qap.num_publics:]]),
                        gl_alphalLtau = Vector([g_l * (alphal * p.evaluate(tau)) for p in self.qap.L[self.qap.num_publics:]]),
                        gr_alpharRtau = Vector([g_r * (alphar * p.evaluate(tau)) for p in self.qap.R[self.qap.num_publics:]]),
                        go_alphaoOtau = Vector([g_o * (alphao * p.evaluate(tau)) for p in self.qap.O[self.qap.num_publics:]]),
                        g_taus = Vector([g * tau.pow(i) for i in range(100)]),
                        glro_betaLROtau = Vector([g_l * (beta * l.evaluate(tau)) + g_r * (beta * r.evaluate(tau)) + g_o * (beta * o.evaluate(tau))
                            for l, r, o in zip(self.qap.L[self.qap.num_publics:],
                                                self.qap.R[self.qap.num_publics:],
                                                self.qap.O[self.qap.num_publics:])]))

        # Verification key
        vk = VerificationKey(g = g,
                             g_alphal = g * alphal, g_alphar = g * alphar, g_alphao = g * alphao,
                             g_gamma = g * gamma, g_betagamma = g * (beta * gamma),
                             gl_Ltau = Vector([g_l * p.evaluate(tau) for p in self.qap.L[:self.qap.num_publics]]),
                             gr_Rtau = Vector([g_r * p.evaluate(tau) for p in self.qap.R[:self.qap.num_publics]]),
                             go_Otau = Vector([g_o * p.evaluate(tau) for p in self.qap.O[:self.qap.num_publics]]),
                             go_Ztau = g_o * self.qap.Z.evaluate(tau))
        
        self.pk = pk
        self.vk = vk

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
        solio = Vector(sol[self.qap.num_publics:])
        
        Lt = self.pk.gl_Ltau.dot(solio) # Multiexp
        Rt = self.pk.gr_Rtau.dot(solio) # Multiexp
        Ot = self.pk.go_Otau.dot(solio) # Multiexp
        aLt = self.pk.gl_alphalLtau.dot(solio) # Multiexp
        aRt = self.pk.gr_alpharRtau.dot(solio) # Multiexp
        aOt = self.pk.go_alphaoOtau.dot(solio) # Multiexp
        bLROt = self.pk.glro_betaLROtau.dot(solio) # Multiexp
        Ht = self.pk.g_taus.dot(H) # Multiexp

        return (Lt,Rt,Ot,aLt,aRt,aOt,bLROt,Ht)

    def verify(self, inps, proof):
        sol = [FieldP(0)] * len(circuit.symbols)
        for k, v in inps.items():
            sol[circuit.symbols[k]] = v
        sol = Vector(sol)
        (Lt,Rt,Ot,aLt,aRt,aOt,bLROt,Ht) = proof

        vLt = self.vk.gl_Ltau.dot(sol) # Multiexp
        vRt = self.vk.gr_Rtau.dot(sol) # Multiexp
        vOt = self.vk.go_Otau.dot(sol) # Multiexp

        l = Lt + vLt
        r = Rt + vRt
        o = Ot + vOt

        div_check = e(l, r) == e(self.vk.go_Ztau, Ht) + e(o, self.vk.g)
        
        lin_check = e(aLt, self.vk.g) == e(Lt, self.vk.g_alphal) and e(aRt, self.vk.g) == e(Rt, self.vk.g_alphar) and e(aOt, self.vk.g) == e(Ot, self.vk.g_alphao)

        coef_check = e(bLROt, self.vk.g_gamma) == e(Lt + Rt + Ot, self.vk.g_betagamma)
        
        return div_check and lin_check and coef_check

if __name__ == '__main__':
    g = CircuitGenerator()

    g.mul('x^2', 'x', 'x')
    g.mul('x^3', 'x^2', 'x')
    g.add('x^3+x', 'x^3', 'x')
    g.add('x^3+x+6', 'x^3+x', FieldP(6))
    g.mul('(x^3+x+6)^2', 'x^3+x+6', 'x^3+x+6')
    circuit = g.compile({'1', '(x^3+x+6)^2'})
    qap = QAP(circuit)
    pino = Pinocchio(qap)

    inputs = {'1': FieldP(1), '(x^3+x+6)^2': FieldP(1296)}

    solution = {'x': FieldP(3),
                'x^2': FieldP(9),
                'x^3': FieldP(27),
                'x^3+x': FieldP(30),
                'x^3+x+6': FieldP(36)}

    proof = pino.prove(inputs, solution)
    print(pino.verify(inputs, proof))
