# Libraries
from dataclasses import dataclass, field, InitVar
from typing import List, Union, Any, Dict


@dataclass
class system:
    memory_size: InitVar[int]
    memory_input: InitVar[List[int]]

    memory_pointer: int = field(default=0, init=False)
    instruction_pointer: int = field(default=0, init=False)
    memory: List[int] = field(default_factory=list, init=False)
    functions: Dict[str, Any] = field(default_factory=dict, init=False, repr=False)
    registered_functions: List[str] = field(default_factory=list, init=False)

    def __post_init__(self, memory_size: int, memory_input: List[int]) -> None:
        """
        Post init
        :param memory_size: Size of the memory
        """
        if len(memory_input) > memory_size:
            raise RuntimeError('Requested memory size is smaller than the given input')
        self.memory = memory_input + [0] * (memory_size - len(memory_input))


# check_range :: Union[List[int], int] -> system -> BaseNode -> bool
def check_range(index: Union[List[int], int], sys: system, node: 'BaseNode') -> bool:
    """
    Function to check if the given index is not outside the memory indexes
    :param index: Index that it is trying to acces
    :param sys: System that will be checked against
    :param node: Node which is running
    :return: Return False if in range
    """
    # Check if it is a list of indexes, if so loop through them all
    if isinstance(index, list):
        return next(filter(lambda list_index: check_range(list_index, sys, node), index), False)

    # Check if index is within the memory
    if index > len(sys.memory) - 1 or index < 0:
        raise RuntimeError(f"Tried accessing outside memory ({index} > {len(sys.memory)}) at row {node.row}")

    # Return false otherwise
    return False

