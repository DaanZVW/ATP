from typing import List, Optional, Any, Dict

# Import HRA Nodes
from interpreter import RightMemoryNode, RightInstructionNode, LeftMemoryNode, LeftInstructionNode, MoveMemoryNode, \
    MoveInstructionNode, MoveMemoryValueNode, PrintNode, FunctionNode, CloseNode, CallNode, ExitNode, GreaterNode, \
    LessNode, EqualNode, UnequalNode, SetNode, IncrementNode, DecrementNode, MultiplyNode, BaseNode
from interpreter import system


# outputReader :: bytes -> str
def outputReader(output: bytes) -> str:
    """
    Used for converting the compiler assembly output to readable string
    :param output: output of the assembly file
    :return: readable string
    """
    align = 4
    return "".join(map(
        lambda index: str(int.from_bytes(output[index * align:(index + 1) * align], 'little')),
        range(0, int(len(output) / align))
    ))


# makeComment :: str -> str
def makeComment(comment: str) -> str:
    """
    Function for generating comments in assembly
    :param comment: Comment
    :return: Comment string for in assembly
    """
    return f'@ {comment}\n'


# makeLabel :: str -> str
def makeLabel(label: str) -> str:
    """
    Function for generating goto labels in assembly
    :param label: Label for goto statement
    :return: Label string for in assembly
    """
    return f"{label}:\n"


# makeIndicator :: str -> Tuple[str] -> str
def makeIndicator(label: str, *arguments: str) -> str:
    """
    Function for generating indicators (.section, .ascii, etc.) in assembly
    :param label: Indicator label
    :param arguments: Arguments for the label
    :return: Indicator string for in assembly
    """
    return f"{label}".ljust(9) + f"{' '.join(arguments)}\n"


# makeInstruction :: str -> Tuple[str] -> str
def makeInstruction(instruction: str, *arguments: str) -> str:
    """
    Function for generating an assembly instruction with arguments
    :param instruction: Assembly instruction
    :param arguments: Arguments for instructions
    :return: Instruction for in assembly
    """
    return f"\t{instruction.upper()}".ljust(6) + f"{', '.join(arguments)}\n"


# compileNodes :: List[BaseNode] -> Dict[str, Any] -> int -> bool -> str
def compileNodes(nodes: List[BaseNode],
                 compilerDefaults: Dict[str, Any],
                 node_index: Optional[int] = 0,
                 verbose: Optional[bool] = True) -> str:
    """
    Function for compiling the given nodes with compilerDefaults
    :param nodes: Nodes to compile
    :param compilerDefaults: Dictionary with settings for compiler
    :param node_index: Index of compiled node (internal only)
    :param verbose: Extra verbose assembly
    :return: Assembly string with all the compiled nodes
    """
    if node_index >= len(nodes):
        return ''
    node = nodes[node_index]

    to_add_str = ''
    # Add extra verbose message inside assembly
    if verbose:
        to_add_str += makeComment(f"node at row {node.row}: {node.name}\n")

    # If main node, add the start_branch identifier
    if compilerDefaults['node_start'] == node.row:
        to_add_str += makeLabel(compilerDefaults['start_branch'])

    to_add_str += makeLabel(f'node_{node.row}')

    # Memory manipulations
    if isinstance(node, RightMemoryNode):
        to_add_str += makeInstruction(
            'sub',
            compilerDefaults['mempointer'],
            f'#{node.move_amount * compilerDefaults["alignment"]}'
        )

    elif isinstance(node, LeftMemoryNode):
        to_add_str += makeInstruction(
            'add',
            compilerDefaults['mempointer'],
            f'#{node.move_amount * compilerDefaults["alignment"]}'
        )

    elif isinstance(node, MoveMemoryNode):
        to_add_str += makeInstruction('mov', compilerDefaults['mempointer'], 'fp')
        to_add_str += makeInstruction(
            'sub',
            compilerDefaults['mempointer'],
            f'#{(node.pointer_pos + 1) * compilerDefaults["alignment"]}'
        )

    elif isinstance(node, MoveMemoryValueNode):
        move_adres = (node.pointer_pos + 1) * compilerDefaults['alignment']
        to_add_str += makeInstruction('ldr', 'r0', f'[{compilerDefaults["mempointer"]}]')
        to_add_str += makeInstruction('str', 'r0', f'[fp, #-{move_adres}]')

    elif isinstance(node, SetNode):
        to_add_str += makeInstruction('mov', 'r0', f'#{node.change_value}')
        to_add_str += makeInstruction('str', 'r0', f'[{compilerDefaults["mempointer"]}]')

    # Value manipulation
    elif isinstance(node, (IncrementNode, DecrementNode, MultiplyNode)):
        if isinstance(node, IncrementNode):
            type_manipulation = 'add'
        elif isinstance(node, DecrementNode):
            type_manipulation = 'sub'
        else:
            type_manipulation = 'mul'

        to_add_str += makeInstruction('ldr', 'r0', f'[{compilerDefaults["mempointer"]}]')
        to_add_str += makeInstruction(type_manipulation, 'r0', f'#{node.change_value}')
        to_add_str += makeInstruction('str', 'r0', f'[{compilerDefaults["mempointer"]}]')

    # Instruction pointer manipulations
    elif isinstance(node, (RightInstructionNode, LeftInstructionNode, MoveInstructionNode)):
        if isinstance(node, RightInstructionNode):
            branch_index = node.row + node.move_amount
        elif isinstance(node, LeftInstructionNode):
            branch_index = node.row - node.move_amount
        else:
            branch_index = node.pointer_pos

        if branch_index < 0 or len(nodes) < branch_index:
            raise SyntaxError(f'At row {node.row}: Goto statement to node {branch_index} does not exist, '
                              f'max available {len(nodes)}')

        to_add_str += makeInstruction('b', f'node_{branch_index}')

    # Function handlers
    elif isinstance(node, FunctionNode):
        to_add_str += makeComment(f'Start of function {node.func_name}')
        to_add_str += '\n\n'
        to_add_str += makeLabel(f'function_{node.func_name}')

    elif isinstance(node, CloseNode):
        to_add_str += makeComment('End of function')
        to_add_str += '\n\n'

    elif isinstance(node, CallNode):
        to_add_str += makeInstruction('bl', f'function_{node.func_name}')

    # Stop running
    elif isinstance(node, ExitNode):
        to_add_str += makeInstruction('b', compilerDefaults["exit_branch"])

    # Printing
    elif isinstance(node, PrintNode):
        to_add_str += makeInstruction('mov', 'r1', 'r4')
        to_add_str += makeInstruction('mov', 'r2', f'#{compilerDefaults["alignment"]}')
        to_add_str += makeInstruction('bl', compilerDefaults['print_branch'])

    # Comparing of values
    elif isinstance(node, (GreaterNode, LessNode, EqualNode, UnequalNode)):
        to_add_str += makeInstruction('ldr', 'r0', f'[fp, #-{(node.lhs + 1) * compilerDefaults["alignment"]}]')
        to_add_str += makeInstruction('ldr', 'r1', f'[fp, #-{(node.rhs + 1) * compilerDefaults["alignment"]}]')
        to_add_str += makeInstruction('cmp', 'r0', 'r1')

        if isinstance(node, GreaterNode):
            branch_condition = 'BGT'
        elif isinstance(node, LessNode):
            branch_condition = 'BLT'
        elif isinstance(node, EqualNode):
            branch_condition = 'BEQ'
        else:
            branch_condition = 'BNE'

        to_add_str += makeInstruction(branch_condition, f'node_{node.row + 1}')
        to_add_str += makeInstruction('b', f'node_{node.row + 2}')

    return to_add_str + compileNodes(nodes, compilerDefaults, node_index + 1, verbose)


# memoryFiller :: List[int] -> int -> int -> str
def memoryFiller(input_mem: List[int], alignment: int, index: int = None) -> str:
    """
    Function for generating the filling of storage when given the argument -i [values]
    :param input_mem: All the integer inputs
    :param alignment: Alignment in assembly file
    :param index: Index of the input
    :return: Assembly string with an input generator
    """
    if not input_mem:
        return ''
    if index is None:
        index = 1

    value, *rest = input_mem
    to_add_str = makeInstruction('mov', 'r0', f'#{value}')
    to_add_str += makeInstruction('str', 'r0', f'[fp, #-{index * alignment}]')

    return to_add_str + memoryFiller(rest, alignment, index + 1)


# compiler :: List[BaseNode] -> system -> str -> List[int] -> Dict[str, Any] -> str
def compiler(nodes: List[BaseNode], sys: system, link_name: str, input_mem: List[int], **kwargs) -> str:
    """
    Main compiler function
    :param nodes: Nodes in the HRA file
    :param sys: Prepared system which has variables that the compiler uses
    :param link_name: Main function name
    :param input_mem: All inputs given from the user
    :param kwargs: Kwargs for the internal compileNodes function
    :return: Assembly string of the file
    """
    compilerDefaults = {
        # Label names
        'exit_branch': '_exit',
        'print_branch': 'show_memory',
        'start_branch': link_name,
        'node_start': sys.instruction_pointer + 1,

        # Register definitions
        'stack_top': 'sp',
        'mempointer': 'r4',
        'stack_bottom': 'fp',

        # Qemu settings
        'kernel_print': '#0x4',
        'kernel_exit': '#0x1',

        # Compiler settings
        'alignment': 4,
        'memory_size': len(sys.memory),
    }

    print_func = ''.join([
        makeLabel(compilerDefaults["print_branch"]),
        makeInstruction('push', '{r0, r7, lr}'),
        makeInstruction('mov', 'r0', '#1'),
        makeInstruction('mov', 'r7', compilerDefaults['kernel_print']),
        makeInstruction('swi', '0'),
        makeInstruction('pop', '{r0, r7, pc}')
    ])

    init = ''.join([
        makeIndicator('.section', '.text'),
        makeIndicator('.global', '_start'),
        makeIndicator('.align', str(compilerDefaults['alignment'])),
        '\n'
    ])

    if input_mem:
        input_instructions = ''.join([
            makeLabel('_input'),
            memoryFiller(input_mem, compilerDefaults['alignment']),
            makeLabel('_start_final')
        ])
    else:
        input_instructions = ''

    start = ''.join([
        makeLabel('_start'),
        makeInstruction('mov', 'fp', 'sp'),
        makeInstruction('mov', 'r4', 'sp'),
        makeInstruction('sub', 'r4', f'#{compilerDefaults["alignment"]}'),
        makeInstruction('sub', 'sp', f'#{compilerDefaults["memory_size"] * compilerDefaults["alignment"]}'),
        input_instructions,
        makeInstruction('b', link_name)
    ])

    exit_func = ''.join([
        makeLabel(compilerDefaults['exit_branch']),
        makeInstruction('mov', 'sp', 'fp'),
        makeInstruction('mov', 'r7', compilerDefaults['kernel_exit']),
        makeInstruction('mov', 'r0', '#1'),
        makeInstruction('swi', '0')
    ])

    inside = compileNodes(nodes, compilerDefaults, **kwargs)

    return init + start + exit_func + '\n' + print_func + '\n' + inside
