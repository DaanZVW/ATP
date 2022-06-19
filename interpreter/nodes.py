from dataclasses import dataclass, field
from typing import List, Tuple
from abc import ABC

from .lexer import found_token
from .system import system


@dataclass
class BaseNode(ABC):
    name: str = field(default='Base', init=False)
    amount_params: Tuple[int] = field(default=None, init=False)

    row: int = field()
    params: List[found_token] = field()

    def __post_init__(self):
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

    def configure(self):
        pass

    def perform(self, sys: system):
        return sys


@dataclass
class PointerAdderBaseNode(BaseNode):
    # Base vars
    amount_params = (1,)

    # Node vars
    move_amount: int = field(init=False)

    def configure(self):
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

    def configure(self):
        self.pointer_pos = int(self.params[0].content)


@dataclass
class RightMemoryNode(PointerAdderBaseNode):
    # Base vars
    name = 'RightMemoryNode'

    def perform(self, sys: system):
        new_pointer = sys.memory_pointer + self.move_amount
        sys.check_range(new_pointer, self)
        sys.memory_pointer = new_pointer
        return sys


@dataclass
class LeftMemoryNode(PointerAdderBaseNode):
    # Base vars
    name = 'LeftMemoryNode'

    def perform(self, sys: system):
        new_pointer = sys.memory_pointer - self.move_amount
        sys.check_range(new_pointer, self)
        sys.memory_pointer = new_pointer
        return sys


@dataclass
class MoveMemoryNode(PointerSetterBaseNode):
    # Base vars
    name = 'MoveMemoryNode'

    def perform(self, sys: system):
        new_pointer = self.pointer_pos
        sys.check_range(new_pointer, self)
        sys.memory_pointer = new_pointer
        return sys


@dataclass
class RightInstructionNode(PointerAdderBaseNode):
    # Base vars
    name = 'RightInstructionNode'

    def perform(self, sys: system):
        sys.instruction_pointer += self.move_amount
        return sys


@dataclass
class LeftInstructionNode(PointerAdderBaseNode):
    # Base vars
    name = 'LeftInstructionNode'

    def perform(self, sys: system):
        sys.instruction_pointer -= self.move_amount
        return sys


@dataclass
class MoveInstructionNode(PointerSetterBaseNode):
    # Base vars
    name = 'MoveInstructionNode'

    def perform(self, sys: system):
        sys.instruction_pointer = self.pointer_pos
        return sys


@dataclass
class PrintNode(BaseNode):
    # Base vars
    name = 'PrintNode'
    amount_params = None

    def perform(self, sys: system):
        print(sys.memory[sys.memory_pointer])
        return sys


@dataclass
class FunctionNode(BaseNode):
    # Base vars
    name = 'FunctionNode'
    amount_params = (1,)

    # Node vars
    func_name: str = field(init=False)
    instruction_index: int = field(init=False, default=0)

    def configure(self):
        self.func_name = self.params[0].content

    def perform(self, sys: system):
        sys.instruction_pointer = self.instruction_index
        return sys


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

    def configure(self):
        self.func_name = self.params[0].content

    def perform(self, sys: system):
        if self.func_name not in sys.functions:
            raise RuntimeError(f"Function '{self.func_name}' not found")
        sys.functions[self.func_name].perform(sys)
        return sys


@dataclass
class CompareBaseNode(BaseNode):
    # Base vars
    amount_params = (2,)

    # Node vars
    lhs: int = field(init=False)
    rhs: int = field(init=False)

    # Base functions
    def configure(self):
        lhs, rhs = self.params
        self.lhs, self.rhs = int(lhs.content), int(rhs.content)

    def perform(self, sys: system):
        sys.check_range([self.lhs, self.rhs], self)

        if self.compare(sys.memory[self.lhs], sys.memory[self.rhs]):
            new_pointer = sys.instruction_pointer
        else:
            new_pointer = sys.instruction_pointer + 1

        sys.instruction_pointer = new_pointer
        return sys

    # Compare function
    def compare(self, lhs, rhs):
        raise RuntimeError("No compare function has been configured")


@dataclass
class GreaterNode(CompareBaseNode):
    # Base vars
    name = 'GreaterNode'

    # Compare function
    def compare(self, lhs, rhs):
        return lhs > rhs


@dataclass
class LessNode(CompareBaseNode):
    # Base vars
    name = 'LessNode'

    # Compare function
    def compare(self, lhs, rhs):
        return lhs < rhs


@dataclass
class EqualNode(CompareBaseNode):
    # Base vars
    name = 'EqualNode'

    # Compare function
    def compare(self, lhs, rhs):
        return lhs == rhs


@dataclass
class SetBaseNode(BaseNode):
    # Node var
    change_value: int = field(init=False)

    def perform(self, sys: system):
        sys.memory[sys.memory_pointer] = self.getValue(sys.memory[sys.memory_pointer])
        return sys

    def getValue(self, mem_value: int):
        raise RuntimeError(f"Node '{self.name}' has no implementation of 'getValue()'")


@dataclass
class IncrementNode(SetBaseNode):
    name = 'IncrementNode'
    amount_params = (1,)

    def configure(self):
        amount = int(self.params[0].content)
        if amount < 1:
            raise SyntaxError(f"Increment amount ({amount}) is below 1")
        self.change_value = amount

    def getValue(self, mem_value: int):
        return mem_value + self.change_value


@dataclass
class DecrementNode(SetBaseNode):
    # Base vars
    name = 'DecrementNode'
    amount_params = (1,)

    def configure(self):
        amount = int(self.params[0].content)
        if amount < 1:
            raise SyntaxError(f"Decrement amount ({amount}) is below 1")
        self.change_value = amount

    def getValue(self, mem_value: int):
        return mem_value - self.change_value


@dataclass
class MultiplyNode(SetBaseNode):
    # Base vars
    name = 'MultiplyNode'
    amount_params = (1,)

    def configure(self):
        amount = int(self.params[0].content)
        if amount < 1:
            raise SyntaxError(f"Decrement amount ({amount}) is below 1")
        self.change_value = amount

    def getValue(self, mem_value: int):
        return mem_value * self.change_value


@dataclass
class ExitNode(BaseNode):
    name = 'ExitNode'
    amount_params = None


