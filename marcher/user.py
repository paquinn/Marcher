# user.py
from marcher.testing import Base


class MyClass(Base):
    def __ini__(self):
        pass

    def settings(self):
        pass

    def draw(self):
        pass
c = MyClass()

def test():
    return "Hello {1+2} world"

print(test())