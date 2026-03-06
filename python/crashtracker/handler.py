import os, signal, random

def handler(event, context):
    from ddtrace.internal.core import crashtracking
    crashtracking.start()

    rand = random.random()
    if rand < 0.33:
        raise RuntimeError("This is a random error to test crash tracking.")
    elif rand < 0.66:
        os.kill(os.getpid(), signal.SIGABRT)
    else:
        os.kill(os.getpid(), signal.SIGSEGV)

if __name__ == "__main__":
    try:
        handler({}, {})
    except Exception as e:
        print(f"Caught an exception: {e}")
