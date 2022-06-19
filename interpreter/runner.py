from .nodes import BaseNode, FunctionNode, CallNode, ExitNode, CloseNode
from .system import system
from typing import List, Iterable
from copy import deepcopy


def makeAST(nodes: List[BaseNode], sys: system):
    """

    :param nodes:
    :param sys:
    :return:
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
    return nodes


def runner(AST_tree: List[BaseNode], sys: system) -> Iterable[system]:
    """

    :param AST_tree:
    :param sys:
    :return:
    """
    # Try to get the instruction, if outside list raise a runtime error
    try:
        execution_node = AST_tree[sys.instruction_pointer]
    except IndexError:
        raise RuntimeError(f"Instruction pointer is outside scope, max available: {len(AST_tree)}, "
                           f"pointer: {sys.instruction_pointer + 1}")

    # Check if instance is
    if isinstance(execution_node, ExitNode):
        return sys

    elif isinstance(execution_node, CallNode):
        yield execution_node.perform(sys)
    else:
        execution_node.perform(sys)
        yield deepcopy(sys)

    sys.instruction_pointer += 1
    yield from runner(AST_tree, sys)

