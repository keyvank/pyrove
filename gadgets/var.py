class Var:
    def __init__(self):
        self.value = None
        self.callback = set()

    def depend(self, callback):
        self.callback.add(callback)

    def assign(self, value):
        if self.value is None:
            self.value = value
            for c in self.callback:
                c(self)
        elif self.value != value:
            raise Exception("Different values are assigned to the variable!")

    def is_assigned(self):
        return self.value is not None
