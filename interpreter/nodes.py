# Libraries
from dataclasses import dataclass, field
from typing import List, Tuple
from abc import ABC

# HRA Files
from .lexer import found_token
from .system import system, check_range


@dataclass
class BaseNode(ABC):
    name: str = field(init=False)
    amount_params: Tuple[int] = field(default=None, init=False)

    row: int = field()
    params: List[found_token] = field(repr=False)

    def __post_init__(self):
        """
        Post init of the class (dataclass)
        :return:
        """
        if not (self.amount_params is None and not self.params or
                isinstance(self.amount_params, tuple) and len(self.params) in self.amount_params or
                len(self.params) == self.amount_params):
            str_params = list(map(lambda param: param.content, self.params))
            str_params_amount = 'no' if self.amount_params is None else ' or '.join(map(str, self.amount_params))
            raise SyntaxError(f'At row {self.row} expected {str_params_amount} parameter(s) but received '
                              f'{len(self.params)} -> {", ".join(str_params) if str_params else None}')

        try:
            self.configure()
        except AttributeError:
            pass

    def configure(self) -> None:
        """
        This function is used to handle the params which is gathered at the __post_init__
        You can see this as additional instructions to init the node and will not be run after it has been initialised
        This way it will stay functional and adds some oversight over the nodes which otherwise will be very abstract
        """
        pass


@dataclass
class PointerAdderBaseNode(BaseNode):
    # Base vars
    amount_params = (1,)

    # Node vars
    move_amount: int = field(init=False)

    def configure(self) -> None:
        """
        Configure the node with the parameters collected in the BaseNode
        """
        if len(self.params) > 0:
            amount = int(self.params[0].content)
            if amount < 1:
                raise SyntaxError(f"Given amount ({amount}) must at least be 1")
            self.move_amount = amount
        else:
            self.move_amount = 1


@dataclass
class PointerSetterBaseNode(BaseNode):
    # Base vars
    amount_params = (1,)

    # Node vars
    pointer_pos: int = field(init=False)

    def configure(self) -> None:
        """
        Configure the node with the parameters collected in the BaseNode
        """
        self.pointer_pos = int(self.params[0].content)


@dataclass
class RightMemoryNode(PointerAdderBaseNode):
    # Base vars
    name = 'RightMemoryNode'


@dataclass
class LeftMemoryNode(PointerAdderBaseNode):
    # Base vars
    name = 'LeftMemoryNode'


@dataclass
class MoveMemoryNode(PointerSetterBaseNode):
    # Base vars
    name = 'MoveMemoryNode'


@dataclass
class MoveMemoryValueNode(PointerSetterBaseNode):
    # Base vars
    name = 'MoveMemoryValueNode'


@dataclass
class RightInstructionNode(PointerAdderBaseNode):
    # Base vars
    name = 'RightInstructionNode'


@dataclass
class LeftInstructionNode(PointerAdderBaseNode):
    # Base vars
    name = 'LeftInstructionNode'


@dataclass
class MoveInstructionNode(PointerSetterBaseNode):
    # Base vars
    name = 'MoveInstructionNode'


@dataclass
class PrintNode(BaseNode):
    # Base vars
    name = 'PrintNode'
    amount_params = None


@dataclass
class FunctionNode(BaseNode):
    # Base vars
    name = 'FunctionNode'
    amount_params = (1,)

    # Node vars
    func_name: str = field(init=False)
    instruction_index: int = field(init=False, default=0)

    def configure(self) -> None:
        """
        Configure the node with the parameters collected in the BaseNode
        """
        self.func_name = self.params[0].content


@dataclass
class CloseNode(BaseNode):
    # Base vars
    name = 'CloseNode'
    amount_params = None


@dataclass
class CallNode(BaseNode):
    # Base vars
    name = 'CallNode'
    amount_params = (1,)

    # Node vars
    func_name: str = field(init=False)

    def configure(self) -> None:
        """
        Configure the node with the parameters collected in the BaseNode
        """
        self.func_name = self.params[0].content


@dataclass
class CompareBaseNode(BaseNode):
    # Base vars
    amount_params = (2,)

    # Node vars
    lhs: int = field(init=False)
    rhs: int = field(init=False)

    # Base functions
    def configure(self) -> None:
        """
        Configure the node with the parameters collected in the BaseNode
        """
        lhs, rhs = self.params
        self.lhs, self.rhs = int(lhs.content), int(rhs.content)


@dataclass
class GreaterNode(CompareBaseNode):
    # Base vars
    name = 'GreaterNode'


@dataclass
class LessNode(CompareBaseNode):
    # Base vars
    name = 'LessNode'


@dataclass
class EqualNode(CompareBaseNode):
    # Base vars
    name = 'EqualNode'


@dataclass
class UnequalNode(CompareBaseNode):
    # Base vars
    name = 'UnequalNode'


@dataclass
class SetBaseNode(BaseNode):
    # Node var
    change_value: int = field(init=False)


@dataclass
class SetNode(SetBaseNode):
    name = 'SetNode'
    amount_params = (1,)

    def configure(self) -> None:
        """
        Configure the node with the parameters collected in the BaseNode
        """
        self.change_value = int(self.params[0].content)


@dataclass
class IncrementNode(SetBaseNode):
    name = 'IncrementNode'
    amount_params = (1,)

    def configure(self) -> None:
        """
        Configure the node with the parameters collected in the BaseNode
        """
        amount = int(self.params[0].content)
        if amount < 1:
            raise SyntaxError(f"Increment amount ({amount}) is below 1")
        self.change_value = amount


@dataclass
class DecrementNode(SetBaseNode):
    # Base vars
    name = 'DecrementNode'
    amount_params = (1,)

    def configure(self) -> None:
        """
        Configure the node with the parameters collected in the BaseNode
        """
        amount = int(self.params[0].content)
        if amount < 1:
            raise SyntaxError(f"Decrement amount ({amount}) is below 1")
        self.change_value = amount


@dataclass
class MultiplyNode(SetBaseNode):
    # Base vars
    name = 'MultiplyNode'
    amount_params = (1,)

    def configure(self) -> None:
        """
        Configure the node with the parameters collected in the BaseNode
        """
        amount = int(self.params[0].content)
        if amount < 1:
            raise SyntaxError(f"Multiply amount ({amount}) is below 1")
        self.change_value = amount


@dataclass
class ExitNode(BaseNode):
    name = 'ExitNode'
    amount_params = None


# perform :: BaseNode -> system -> system
def perform(node: BaseNode, sys: system) -> system:
    """
    Perform the node on the given system and return its state
    :param node: Node that will be ran
    :param sys: System where it will be ran on
    :return: the new system
    """
    # Handle memory shifters
    if isinstance(node, (RightMemoryNode, LeftMemoryNode, MoveMemoryNode)):
        if isinstance(node, RightMemoryNode):
            func = lambda pointer: pointer + node.move_amount
        elif isinstance(node, LeftMemoryNode):
            func = lambda pointer: pointer - node.move_amount
        else:
            func = lambda _: node.pointer_pos

        new_pointer = func(sys.memory_pointer)
        check_range(new_pointer, sys, node)
        sys.memory_pointer = new_pointer

    # Handle instruction shifters
    # Reason for extra int manipulations is because the runner will add 1 to the instruction_pointer
    # by every iteration over the nodes therefor these extra -1 and +1 are needed
    elif isinstance(node, (RightInstructionNode, LeftInstructionNode, MoveInstructionNode)):
        if isinstance(node, RightInstructionNode):
            func = lambda pointer: pointer + (node.move_amount - 1)
        elif isinstance(node, LeftInstructionNode):
            func = lambda pointer: pointer - (node.move_amount + 1)
        else:
            func = lambda _: (node.move_amount - 1)

        sys.instruction_pointer = func(sys.instruction_pointer)

    # Handle memory mover
    elif isinstance(node, MoveMemoryValueNode):
        check_range(node.pointer_pos, sys, node)
        sys.memory[node.pointer_pos] = sys.memory[sys.memory_pointer]

    # Handle print
    elif isinstance(node, PrintNode):
        print(sys.memory[sys.memory_pointer])

    # Handle function
    elif isinstance(node, FunctionNode):
        sys.instruction_pointer = node.instruction_index

    # Handle function caller
    elif isinstance(node, CallNode):
        if node.func_name not in sys.functions:
            raise RuntimeError(f"Function '{node.func_name}' not found")
        return perform(sys.functions[node.func_name], sys)

    # Handle all comparisons
    elif isinstance(node, (GreaterNode, LessNode, EqualNode, UnequalNode)):
        if isinstance(node, GreaterNode):
            func = lambda rhs, lhs: rhs > lhs
        elif isinstance(node, LessNode):
            func = lambda rhs, lhs: rhs < lhs
        elif isinstance(node, EqualNode):
            func = lambda rhs, lhs: rhs == lhs
        else:
            func = lambda rhs, lhs: rhs != lhs

        check_range([node.lhs, node.rhs], sys, node)

        if func(sys.memory[node.lhs], sys.memory[node.rhs]):
            new_pointer = sys.instruction_pointer
        else:
            new_pointer = sys.instruction_pointer + 1

        sys.instruction_pointer = new_pointer

    # Handle all memory value manipulators
    elif isinstance(node, (SetNode, IncrementNode, DecrementNode, MultiplyNode)):
        if isinstance(node, SetNode):
            func = lambda _: node.change_value
        elif isinstance(node, IncrementNode):
            func = lambda value: value + node.change_value
        elif isinstance(node, DecrementNode):
            func = lambda value: value - node.change_value
        else:
            func = lambda value: value * node.change_value

        sys.memory[sys.memory_pointer] = func(sys.memory[sys.memory_pointer])

    # Return new system state
    return sys
