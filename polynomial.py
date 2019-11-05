from fieldp import FieldP
from vector import Vector

class PolynomialP:

    def __init__(self, coefs):
        self.coefs = coefs if coefs else [FieldP(0)]

    def __add__(self, p):
        cnt = max(len(self.coefs), len(p.coefs))
        coefs = [FieldP(0)] * cnt
        for i in range(cnt):
            coefs[i] += self.coefs[i] if len(self.coefs) > i else FieldP(0)
            coefs[i] += p.coefs[i] if len(p.coefs) > i else FieldP(0)
        return PolynomialP(coefs)

    def __neg__(self):
        return PolynomialP([-c for c in self.coefs])

    def __sub__(self, p):
        return self + (-p)

    def __mul__(self, p):
        if type(p) is Vector:
            return PolynomialP([p * v for p, v in zip(self.coefs, p.vals)])
        if type(p) is FieldP:
            return PolynomialP([c * p for c in self.coefs])
        cnt = len(self.coefs) + len(p.coefs) - 1
        coefs = [FieldP(0)] * cnt
        for i, coef1 in enumerate(self.coefs):
            for j, coef2 in enumerate(p.coefs):
                coefs[i + j] += coef1 * coef2
        return PolynomialP(coefs)

    def __truediv__(self, p):
        num = self.normalized().coefs
        den = p.normalized().coefs
        if len(num) >= len(den):
            shiftlen = len(num) - len(den)
            den = [FieldP(0)] * shiftlen + den
        else:
            return PolynomialP(num).normalized()
        quot = []
        divisor = den[-1]
        for i in range(shiftlen + 1):
            mult = num[-1] / divisor
            quot = [mult] + quot
            if mult != FieldP(0):
                d = [mult * u for u in den]
                num = [u - v for u, v in zip(num, d)]
            num.pop()
            den.pop(0)
        return PolynomialP(quot).normalized()

    def normalized(self):
        coefs = list(self.coefs)
        while coefs and coefs[-1] == FieldP(0):
            coefs.pop()
        return PolynomialP(coefs)

    def z(length):
        p = PolynomialP([FieldP(1)])
        for i in range(1, length + 1):
            p *= PolynomialP([FieldP(-i), FieldP(1)])
        return p

    def singleton(at, height, length):
        p = PolynomialP([FieldP(1)])
        for i in range(1, length + 1):
            if i != at:
                p *= PolynomialP([FieldP(-i), FieldP(1)])
        p *= height / p.evaluate(FieldP(at))
        return p

    def interpolate(vals):
        p = PolynomialP([FieldP(0)])
        l = len(vals)
        for i, v in enumerate(vals):
            p += PolynomialP.singleton(i + 1, v, l)
        return p

    def evaluate(self, x):
        sm = FieldP(0)
        for i, coef in enumerate(self.coefs):
            sm += coef * x.pow(i)
        return sm

    def __str__(self):
        return ' + '.join(["{}x^{}".format(coef, deg) for deg,coef in enumerate(self.coefs)])
