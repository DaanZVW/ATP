# Libraries
from typing import List, Tuple
import os

# HRA files
from .lexer import lexer
from .parser import parser
from .system import system
from .runner import makeAST
from .nodes import BaseNode


# prepare_interpreter :: str -> int -> List[int] -> Tuple[List[BaseNode], system]
def prepare_interpreter(filename: str, memory_size: int, memory_input: List[int]) -> Tuple[List[BaseNode], system]:
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
    return makeAST(nodes, sys)

