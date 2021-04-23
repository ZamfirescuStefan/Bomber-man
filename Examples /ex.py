class B:
    def __init__(self):
        mem1 = 1


class A:
    def __init__(self):
        self.a = 0
        self.b = 0
        self.b_obj = B()


def addone(ob):
    ob.a += 1


ob = A()
ob.b_obj.mem1 = 23
aux = ob.b_obj

print(aux.mem1)