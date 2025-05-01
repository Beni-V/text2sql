class Singleton(type):
    """
    A metaclass that can be used to create singleton classes.
    Example usage:
        class MyClass(metaclass=Singleton):
            pass
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
