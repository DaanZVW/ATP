from typing import List, Optional

from interpreter import RightMemoryNode, RightInstructionNode, LeftMemoryNode, LeftInstructionNode, MoveMemoryNode, \
    MoveInstructionNode, MoveMemoryValueNode, PrintNode, FunctionNode, CloseNode, CallNode, ExitNode, GreaterNode, \
    LessNode, EqualNode, UnequalNode, SetNode, IncrementNode, DecrementNode, MultiplyNode, BaseNode


def compiler(nodes: List[BaseNode], file_str: Optional[str] = None):
    node, *rest = nodes

    print(node)

    if not len(rest):
        return file_str
    return compiler(rest, file_str)




