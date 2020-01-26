exobj = None

def hello():
    exobj.hello()
    return

def goodbye():
    exobj.goodbye()
    return

class exampleObj:
    def __init__(self):
        return

    def __enter__(self):
        print("entered")
        global exobj
        exobj = self
        return

    def __exit__(self, exc_type, exc_value, traceback):
        print("exited")

    def hello(self):
        print("Hello");

    def goodbye(self):
        print("Goodbye")