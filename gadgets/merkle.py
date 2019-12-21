from .gadget import Gadget, Mul
from fieldp import FieldP
from .mimc import MiMC

class MerkleTree(Gadget):
    def __init__(self, circuit, leaves):
        self.leaves = leaves
        cur = list(leaves)
        while len(cur) != 1:
            nl = []
            for i in range(len(cur)//2):
                ml = Mul(circuit, cur[2*i], cur[2*i+1]).output()
                hashed = MiMC(circuit, ml).output()
                nl.append(hashed)
            cur = nl
        self.root = cur[0]
        super().__init__(circuit, set(leaves))

    def output(self):
        return self.root

    def evaluate(self):
        pass
