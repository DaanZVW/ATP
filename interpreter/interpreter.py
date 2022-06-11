from dataclasses import dataclass, InitVar, field
from typing import List
import os

from .lexer import lexer
from .parser import parser
from .system import system
from .runner import runner, makeAST


@dataclass
class interpreter:
    filename: str
    memory_size: InitVar[int]
    generator: runner = field(init=False)

    def __post_init__(self, memory_size: int):
        if not os.path.isfile(self.filename):
            raise FileNotFoundError(f"Filename {self.filename} does not exist")

        with open(self.filename, 'r') as file:
            file_content = file.read()

        tokens = lexer(file_content)
        nodes = parser(tokens)
        sys = system(memory_size)
        AST_Tree = makeAST(nodes, sys)
        self.generator = runner(AST_Tree, sys)

    def getFinalState(self) -> system:
        *_, final_state = iter(self.generator)
        return final_state

    def getAllStates(self) -> List[system]:
        return list(self.generator)



