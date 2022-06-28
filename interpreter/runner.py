# Libraries
from typing import List, Tuple
from copy import deepcopy

# HRA files
from .nodes import RightMemoryNode, RightInstructionNode, LeftMemoryNode, LeftInstructionNode, MoveMemoryNode, \
    MoveInstructionNode, MoveMemoryValueNode, PrintNode, FunctionNode, CloseNode, CallNode, ExitNode, GreaterNode, \
    LessNode, EqualNode, UnequalNode, SetNode, IncrementNode, DecrementNode, MultiplyNode, BaseNode
from .decorator import run_generator
from .system import system, check_range


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

    if functions:
        # Register the functions in the virtual system
        sys.functions = dict(map(lambda node: (node.func_name, node,), functions))

        # Register only the strings for debugging purposes while printing the system
        sys.registered_functions = list(sys.functions.keys())

        # Set the instruction pointer to the first non function node
        sys.instruction_pointer = next(filter(lambda node: isinstance(node, CloseNode),
                                              nodes[sys.functions[sys.registered_functions[-1]].row:])).row
    else:
        sys.instruction_pointer = 0

    return nodes, sys


# perform :: BaseNode -> system -> system
def perform(node: BaseNode, sys: system) -> system:
    """
    Perform the node on the given system and return its state
    :param node: Node that will be ran
    :param sys: System where it will be ran on
    :return: the new system
    """
    # Handle memory shifters
    if isinstance(node, (RightMemoryNode, LeftMemoryNode, MoveMemoryNode)):
        if isinstance(node, RightMemoryNode):
            func = lambda pointer: pointer + node.move_amount
        elif isinstance(node, LeftMemoryNode):
            func = lambda pointer: pointer - node.move_amount
        else:
            func = lambda _: node.pointer_pos

        new_pointer = func(sys.memory_pointer)
        check_range(new_pointer, sys, node)
        sys.memory_pointer = new_pointer

    # Handle instruction shifters
    # Reason for extra int manipulations is because the runner will add 1 to the instruction_pointer
    # by every iteration over the nodes therefor these extra -1 and +1 are needed
    elif isinstance(node, (RightInstructionNode, LeftInstructionNode, MoveInstructionNode)):
        if isinstance(node, RightInstructionNode):
            func = lambda pointer: pointer + (node.move_amount - 1)
        elif isinstance(node, LeftInstructionNode):
            func = lambda pointer: pointer - (node.move_amount + 1)
        else:
            func = lambda _: (node.pointer_pos - 2)

        sys.instruction_pointer = func(sys.instruction_pointer)

    # Handle memory mover
    elif isinstance(node, MoveMemoryValueNode):
        check_range(node.pointer_pos, sys, node)
        sys.memory[node.pointer_pos] = sys.memory[sys.memory_pointer]

    # Handle print
    elif isinstance(node, PrintNode):
        print(sys.memory[sys.memory_pointer], end='')

    # Handle function
    elif isinstance(node, FunctionNode):
        sys.instruction_pointer = node.instruction_index

    # Handle function caller
    elif isinstance(node, CallNode):
        if node.func_name not in sys.functions:
            raise RuntimeError(f"Function '{node.func_name}' not found")
        return perform(sys.functions[node.func_name], sys)

    # Handle all comparisons
    elif isinstance(node, (GreaterNode, LessNode, EqualNode, UnequalNode)):
        if isinstance(node, GreaterNode):
            func = lambda rhs, lhs: rhs > lhs
        elif isinstance(node, LessNode):
            func = lambda rhs, lhs: rhs < lhs
        elif isinstance(node, EqualNode):
            func = lambda rhs, lhs: rhs == lhs
        else:
            func = lambda rhs, lhs: rhs != lhs

        check_range([node.lhs, node.rhs], sys, node)

        if func(sys.memory[node.lhs], sys.memory[node.rhs]):
            new_pointer = sys.instruction_pointer
        else:
            new_pointer = sys.instruction_pointer + 1

        sys.instruction_pointer = new_pointer

    # Handle all memory value manipulators
    elif isinstance(node, (SetNode, IncrementNode, DecrementNode, MultiplyNode)):
        if isinstance(node, SetNode):
            func = lambda _: node.change_value
        elif isinstance(node, IncrementNode):
            func = lambda value: value + node.change_value
        elif isinstance(node, DecrementNode):
            func = lambda value: value - node.change_value
        else:
            func = lambda value: value * node.change_value

        sys.memory[sys.memory_pointer] = func(sys.memory[sys.memory_pointer])

    # Return new system state
    return sys


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

