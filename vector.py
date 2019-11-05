class Vector:

    def __init__(self, vals):
        self.vals = tuple(vals)

    def __add__(self, v):
        if len(v) != len(self):
            raise Exception("Vector lengths should be equal!")
        return Vector(tuple(v1 + v2 for v1, v2 in zip(self.vals, v.vals)))

    def __neg__(self):
        return Vector(tuple(-v for v in self.vals))

    def __sub__(self, v):
        return self + (-v)

    def __mul__(self, v):
        if type(v) is Vector:
            return Vector(tuple(v1 * v2 for v1, v2 in zip(self.vals, v.vals)))
        else:
            return Vector(tuple(val * v for val in self.vals))

    def dot(self, v):
        from fieldp import FieldP
        return sum(tuple(v1 * v2 for v1, v2 in zip(self.vals, v.vals)), FieldP(0))

    def __getitem__(self, index):
        return self.vals[index]

    def __len__(self):
        return len(self.vals)

    def __str__(self):
        return str(self.vals)

    def __repr__(self):
        return str(self.vals)
