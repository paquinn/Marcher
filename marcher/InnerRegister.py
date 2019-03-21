
class A:
    class inner:
        def __init__(self, name, greeting):
            self.name = name
            self.greeting = greeting

        def __str__(self):
            return self.greeting+" "+self.name

    def wrapper(self, greeting):
        return self.__class__.inner(self.name, greeting)

    @classmethod
    def register(cls, fn):
        a = cls('Bob')
        return a.wrapper

    def __init__(self, name):
        self.name = name


class B(A):
    class inner(A.inner):

        def __str__(self):
            return self.greeting+"&"+self.name


class C(A):
    def wrapper(self):
        return super().wrapper("Hallo")


@A.register
def comp():
    print('complicated')

s1 = comp("Hello")

print(s1)