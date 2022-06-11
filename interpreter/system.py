from dataclasses import dataclass, field, InitVar
from typing import List, Union, Any, Dict


@dataclass
class system:
    memory_size: InitVar[int]

    pointer: int = field(default=0, init=False)
    memory: List[int] = field(default_factory=list, init=False)
    functions: Dict[str, Any] = field(default_factory=dict, init=False, repr=False)
    registered_functions: List[str] = field(default_factory=list, init=False)

    def __post_init__(self, memory_size: int):
        self.memory = [0] * memory_size

    def check_range(self, index: Union[List[int], int], node):
        if isinstance(index, list):
            return next(filter(lambda list_index: self.check_range(list_index, node), index), False)

        if index > len(self.memory) - 1 or index < 0:
            raise RuntimeError(f"Tried accessing outside memory at row {node.row}")

        return False

