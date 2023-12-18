import gc

gc.set_debug(gc.DEBUG_STATS)

class A(object):
    def a(self):
        return self.b()

    def b(self):
        return B().b()

class B(object):
    class C(object):
        pass

    def a(self):
        return A().a()

    def b(self):
        return self.a()

def main():
    a_list = []
    for i in xrange(10):
        a = A()
        a_list.append(a)
    print gc.get_referents(a_list)


if __name__ == '__main__':
    main()
