# Libraries
from typing import List, Any


def run_generator(func):
    """
    Function for running generators
    :param func: Generator
    :return: List of all states
    """
    def inner(*args) -> List[Any]:
        generator = func(*args)
        return list(generator)
    return inner

