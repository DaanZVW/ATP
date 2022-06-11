from .nodes import BaseNode, FunctionNode
from .system import system
from typing import List


def runner(nodes: List[BaseNode], sys: system):
    functions = list(filter(lambda p_node: isinstance(p_node, FunctionNode), nodes))
    sys.functions = dict(map(lambda t_node: (t_node.func_name, t_node,), functions))

    for node in nodes:
        node.perform(sys)

