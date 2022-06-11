from typing import List

from .nodes import *
from .lexer import tokens, found_token


tokenNodeLinker = {
    tokens.RIGHT:     RightNode,
    tokens.LEFT:      LeftNode,
    tokens.MOVE:      MoveNode,
    tokens.PRINT:     PrintNode,
    tokens.FUNCTION:  FunctionNode,
    tokens.CLOSE:     CloseNode,
    tokens.CALL:      CallNode,
    tokens.GREATER:   GreaterNode,
    tokens.LESS:      LessNode,
    tokens.EQUAL:     EqualNode,
    tokens.INCREMENT: IncrementNode,
    tokens.DECREMENT: DecrementNode,
    tokens.MULTIPLY:  MultiplyNode
}


def parser(found_tokens: List[List[found_token]]) -> List[BaseNode]:
    found_nodes = list(map(
        lambda row: tokenNodeLinker[row[0].token](
            row=row[0].row, params=row[1:]
        ), found_tokens
    ))
    return found_nodes


def parseNodes(nodes: List[BaseNode], function_names: List[str] = None):
    if function_names is None:
        function_names = []

    if not nodes:
        return []

    node, *rest = nodes
    if isinstance(node, FunctionNode):
        if node.func_name in function_names:
            raise SyntaxError(f"Function name of {node.func_name} defined at line {node.row} is already in use")

        close_node = next(filter(lambda p_node: isinstance(p_node[1], CloseNode), enumerate(rest)), None)
        if close_node is None:
            raise SyntaxError(f"Function {node.func_name} defined at line {node.row} has no 'close'")

        func_body = rest[:close_node[0]]
        if not func_body:
            raise SyntaxError(f"Function {node.func_name} defined at line {node.row} is empty")

        node.register_body(func_body)
        function_names.append(node.func_name)
        return [node] + parseNodes(rest[close_node[0] + 1:], function_names)

    else:
        return [node] + parseNodes(rest, function_names)
