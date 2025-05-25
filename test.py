class my_class:
    _protected = int()
    __salary =  599
    def __init__(self):
        self._protected = 5
    
obj = my_class()
print(obj._protected)
print(obj._my_class__salary)