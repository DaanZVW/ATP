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


def parseTokens(found_tokens: List[List[found_token]]) -> List[BaseNode]:
    # Return empty list when end of list has been reached
    if len(found_tokens) <= 0:
        return []

    # Split the tokens
    (first, *other_tokens), *rest = found_tokens

    # Raise error when token is not defined
    if first.token not in tokenNodeLinker:
        raise SyntaxError(f"Given key '{first.content}' not a instruction")

    # Return the nodes of given tokens
    return [tokenNodeLinker[first.token](row=first.row, params=other_tokens)] + parseTokens(rest)


def parseNodes(nodes: List[BaseNode], function_names: List[str] = None) -> List[BaseNode]:
    if function_names is None:
        function_names = []

    if not nodes:
        return []

    node, *rest = nodes
    if isinstance(node, FunctionNode):
        # Check if function name already exists
        if node.func_name in function_names:
            raise SyntaxError(f"Function name of {node.func_name} defined at line {node.row} is already in use")

        # Check if function is closed
        close_node = next(filter(lambda p_node: isinstance(p_node[1], CloseNode), enumerate(rest)), None)
        if close_node is None:
            raise SyntaxError(f"Function {node.func_name} defined at line {node.row} has no 'close'")

        # Check if function has a body
        func_body = rest[:close_node[0]]
        if not func_body:
            raise SyntaxError(f"Function {node.func_name} defined at line {node.row} is empty")

        # Register the body to the function node and continue with the parsing
        node.register_body(func_body)
        function_names.append(node.func_name)
        return [node] + parseNodes(rest[close_node[0] + 1:], function_names)

    else:
        return [node] + parseNodes(rest, function_names)


def parser(found_tokens: List[List[found_token]]) -> List[BaseNode]:
    return parseNodes(parseTokens(found_tokens))

