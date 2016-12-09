import newrelic
from newrelic.common.object_names import callable_name

print(newrelic.version)

# DJANGO EXAMPLE

class Parent(object):
    def example_function(self):
        pass

class Child(Parent):
    pass

instance = Child().example_function
print(callable_name(instance))


# FLASK EXAMPLE

def parent():
    def child():
        pass
    return child

instance = parent()
print(callable_name(instance))


# CACHING EXAMPLE

class Mommy(object):
    def lollipop(self):
        pass

class Baby(Mommy):
    pass

parent_instance = Mommy().lollipop
child_instance = Baby().lollipop
print(callable_name(parent_instance))
print(callable_name(child_instance))
