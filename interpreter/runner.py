# Libraries
from typing import List, Tuple
from copy import deepcopy

# HRA files
from .nodes import BaseNode, FunctionNode, ExitNode, CloseNode, perform
from .decorator import run_generator
from .system import system


# makeAST :: List[BaseNode] -> system -> Tuple[List[BaseNode], system]
def makeAST(nodes: List[BaseNode], sys: system) -> Tuple[List[BaseNode], system]:
    """
    Configure the sys with given nodes so the runner has everything that it needs
    :param nodes: List of nodes
    :param sys: System which needs updating
    :return: nodes and the updated system
    """
    # Filter all functions from nodes
    functions = list(filter(lambda node: isinstance(node, FunctionNode), nodes))

    # Register the functions in the virtual system
    sys.functions = dict(map(lambda node: (node.func_name, node,), functions))

    # Register only the strings for debugging purposes while printing the system
    sys.registered_functions = list(sys.functions.keys())

    # Set the instruction pointer to the first non function node
    sys.instruction_pointer = next(filter(lambda node: isinstance(node, CloseNode),
                                          nodes[sys.functions[sys.registered_functions[-1]].row:])).row
    return nodes, sys


# runner :: List[BaseNode] -> system -> List[system]
@run_generator
def runner(AST_tree: List[BaseNode], sys: system) -> List[system]:
    """
    Run the AST_Tree alongside the virtual system. This function itself is a generator function because
    we can return the virtual system (state) every execution of a node. The decorator @run_generator will
    run the generator and return the list of all states before it has received the ExitNode.
    :param AST_tree: Nodes to execute
    :param sys: Virtual system
    :return: List of all the states
    """
    # Try to get the instruction, if outside list raise a runtime error
    try:
        execution_node = AST_tree[sys.instruction_pointer]
    except IndexError:
        raise RuntimeError(f"Instruction pointer is outside scope, max available: {len(AST_tree)}, "
                           f"pointer: {sys.instruction_pointer + 1}")

    # Check if instance is
    if isinstance(execution_node, ExitNode):
        return deepcopy(sys)

    else:
        yield deepcopy(perform(execution_node, sys))

    sys.instruction_pointer += 1
    yield from runner(AST_tree, sys)

