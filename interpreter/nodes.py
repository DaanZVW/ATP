# Libraries
from dataclasses import dataclass, field
from typing import List, Tuple
from abc import ABC

# HRA Files
from .lexer import found_token


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

