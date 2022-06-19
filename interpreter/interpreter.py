# Libraries
from typing import List
import os

# HRA files
from .lexer import lexer
from .parser import parser
from .system import system
from .runner import runner, makeAST


# interpreter :: str -> int -> List[int] -> List[system]
def interpreter(filename: str, memory_size: int, memory_input: List[int]) -> List[system]:
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"Filename {filename} does not exist")

    with open(filename, 'r') as file:
        file_content = file.read()

    # Get the tokens
    tokens = lexer(file_content)
    # Convert tokens to nodes
    nodes = parser(tokens)
    # Make virtual system
    sys = system(memory_size, memory_input)
    # Make AST_Tree
    AST_Tree, sys = makeAST(nodes, sys)
    # Get the states while running
    return runner(AST_Tree, sys)


