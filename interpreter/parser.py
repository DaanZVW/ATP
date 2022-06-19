from typing import List

from .nodes import *
from .lexer import tokens, found_token


tokenNodeLinker = {
    tokens.RIGHT_MEM: RightMemoryNode,
    tokens.RIGHT_INS: RightInstructionNode,
    tokens.LEFT_MEM:  LeftMemoryNode,
    tokens.LEFT_INS:  LeftInstructionNode,
    tokens.MOVE_MEM:  MoveMemoryNode,
    tokens.MOVE_INS:  MoveInstructionNode,
    tokens.PRINT:     PrintNode,
    tokens.FUNCTION:  FunctionNode,
    tokens.CLOSE:     CloseNode,
    tokens.CALL:      CallNode,
    tokens.EXIT:      ExitNode,
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


def parseNodes(nodes: List[BaseNode], index: int = 0, function_names: List[str] = None) -> List[BaseNode]:
    if function_names is None:
        function_names = []

    if len(nodes) <= index:
        return []

    node = nodes[index]
    if isinstance(node, FunctionNode):
        # Check if function name already exists
        if node.func_name in function_names:
            raise SyntaxError(f"Function name of {node.func_name} defined at line {node.row} is already in use")

        # Check if function is closed
        close_node = next(filter(lambda p_node: isinstance(p_node[1], CloseNode), enumerate(nodes[index:])), None)
        if close_node is None:
            raise SyntaxError(f"Function {node.func_name} defined at line {node.row} has no 'close'")

        # Configure the function node
        node.instruction_index = index
        node.function_close = close_node

        # Append the function name
        function_names.append(node.func_name)

    return [node] + parseNodes(nodes, index+1, function_names)


def parser(found_tokens: List[List[found_token]]) -> List[BaseNode]:
    nodes = parseTokens(found_tokens)
    if not next(filter(lambda node: isinstance(node, ExitNode), nodes), False):
        raise SyntaxError("No 'exit' found in file")
    return parseNodes(nodes)

