from newrelic.common.object_names import callable_name

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
