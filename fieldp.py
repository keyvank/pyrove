class FieldP:
    P = 0x73eda753299d7d483339d80809a1d80553bda402fffe5bfeffffffff00000001

    def zero():
        return FieldP(0)

    def __init__(self, value):
        self.value = value % FieldP.P

    def __add__(self, other):
        return FieldP((self.value + other.value) % FieldP.P)

    def __sub__(self, other):
        return FieldP((self.value - other.value) % FieldP.P)

    def __mul__(self, other):
        return FieldP((self.value * other.value) % FieldP.P)

    def __truediv__(self, other):
        return FieldP(
            (self.value * pow(other.value, FieldP.P - 2, FieldP.P)) % FieldP.P)

    def __neg__(self):
        return FieldP((-self.value) % FieldP.P)

    def __eq__(self, other):
        return type(self) == type(other) and self.value == other.value

    def pow(self, other):
        return FieldP(pow(self.value, other, FieldP.P))

    def __repr__(self):
        return "FieldP({})".format(self.value)

    def __str__(self):
        return "FieldP({})".format(self.value)
