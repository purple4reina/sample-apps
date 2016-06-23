"""
Several methods that transform strings from one thing to another
"""

def hello_to_goodbye(string):
    """
    Transform:
        "Hello" to "Goodbye"
        "hello" to "goodbye"
    """
    return string.replace('hello', 'goodbye').replace('Hello', 'Goodbye')
