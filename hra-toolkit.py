import argparse

from interpreter import interpreter

if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser(description='CLI for the HRA toolkit')
    required = cli_parser.add_argument_group('required arguments')
    required.add_argument('-f', '--file', type=str, required=True,
                          help='Location of the file')
    required.add_argument('-m', '--memsize', default=32,
                          metavar='SIZE', help='Allocate the size of the memory')

    select = cli_parser.add_mutually_exclusive_group(required=True)
    select.add_argument('-i', '--interpreter', action='store_true',
                        help='Run the interpreter on given file')
    select.add_argument('-c', '--compiler', action='store_true',
                        help='Run the compiler on given file')

    optional = cli_parser.add_argument_group('optional arguments')
    optional.add_argument('-s', '--state', type=str, choices=['final', 'all'], default='final',
                          help='Print the type of state of the virtual system')
    optional.add_argument('-o', '--output', type=str,
                          help='Destination file of the assembly')

    # Execute the parse_args() method
    args = vars(cli_parser.parse_args())

    # Get interpreter
    inter = interpreter(filename=args.get('file'), memory_size=args.get('memsize'))

    # Print state
    try:
        if args.get('state') != 'final':
            print(*inter.getAllStates(), sep='\n')
        else:
            print(inter.getFinalState())
    except RecursionError:
        raise RecursionError(f"File {args.get('file')} has exceeded the maximum recursion depth")

