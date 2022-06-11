from .nodes import BaseNode, FunctionNode
from .system import system
from typing import List, Iterable


def makeAST(nodes: List[BaseNode], sys: system):
    functions = list(filter(lambda node: isinstance(node, FunctionNode), nodes))
    sys.functions = dict(map(lambda node: (node.func_name, node,), functions))
    sys.registered_functions = list(map(lambda node: node.func_name, functions))
    AST_t = list(filter(lambda node: not isinstance(node, FunctionNode), nodes))
    return AST_t


def runner(AST_tree: List[BaseNode], sys: system) -> Iterable[system]:
    if len(AST_tree) <= 0:
        return sys

    first, *rest = AST_tree
    first.perform(sys)
    yield sys
    yield from runner(rest, sys)

