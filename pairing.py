# Naive pairing

from fieldp import FieldP


class G1:
    GENERATOR = FieldP(2)

    def __init__(self, val=None):
        self.value = val if val else G1.GENERATOR

    def __add__(self, other):
        ret = G1(self.value)
        ret.value += other.value
        return ret

    def __mul__(self, other):
        ret = G1(self.value)
        ret.value *= other
        return ret

    def __eq__(self, other):
        return type(self) == type(other) and self.value == other.value

    def __str__(self):
        return "G1({})".format(self.value)

    def __repr__(self):
        return str(self)


class G2:
    GENERATOR = FieldP(3)

    def __init__(self, val=None):
        self.value = val if val else G2.GENERATOR

    def __add__(self, other):
        ret = G2(self.value)
        ret.value += other.value
        return ret

    def __mul__(self, other):
        ret = G2(self.value)
        ret.value *= other
        return ret

    def __eq__(self, other):
        return type(self) == type(other) and self.value == other.value

    def __str__(self):
        return "G2({})".format(self.value)

    def __repr__(self):
        return str(self)


class GT:
    GENERATOR = FieldP(5)

    def __init__(self, val=None):
        self.value = val if val else GT.GENERATOR

    def __add__(self, other):
        ret = GT(self.value)
        ret.value += other.value
        return ret

    def __mul__(self, other):
        ret = GT(self.value)
        ret.value *= other
        return ret

    def __eq__(self, other):
        return type(self) == type(other) and self.value == other.value

    def __str__(self):
        return "GT({})".format(self.value)

    def __repr__(self):
        return str(self)


def e(a, b):
    ret = GT()
    ret *= a.value * b.value
    return ret


if __name__ == '__main__':
    g1 = G1() * FieldP(4)
    g2 = G2() * FieldP(8)

    print(e(g1, g2))
