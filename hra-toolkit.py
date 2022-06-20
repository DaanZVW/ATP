# Libraries
import argparse

# HRA Files
from interpreter import interpreter


if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser(description='CLI for the HRA toolkit')
    required = cli_parser.add_argument_group('required arguments')
    required.add_argument('-f', '--file', type=str, required=True,
                          help='Location of the file')
    required.add_argument('-m', '--memsize', default=32,
                          metavar='SIZE', help='Allocate the size of the memory')

    select = cli_parser.add_mutually_exclusive_group(required=True)
    select.add_argument('-it', '--interpreter', action='store_true',
                        help='Run the interpreter on given file')
    # select.add_argument('-c', '--compiler', action='store_true',
    #                     help='Run the compiler on given file')

    optional = cli_parser.add_argument_group('optional arguments')
    optional.add_argument('-s', '--state', type=str, choices=['final', 'all', 'none'], default='none',
                          help='Print the type of state of the virtual system')
    # optional.add_argument('-o', '--output', type=str,
    #                       help='Destination file of the assembly')
    optional.add_argument('-i', '--input', type=int, default=[], nargs='+',
                          help='Input for running the file, order of inputs is the same as in memory')

    # Execute the parse_args() method
    args = vars(cli_parser.parse_args())

    # Get interpreter
    states = interpreter(filename=args.get('file'), memory_size=args.get('memsize'), memory_input=args.get('input'))

    # Print state
    if args.get('state') == 'all':
        print(*states, sep='\n')

    elif args.get('state') == 'final':
        *_, final_state = states
        print(final_state)
        
    print(f'Output: {states[-1].memory[0]}')



