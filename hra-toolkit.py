# Libraries
import os
import argparse
import subprocess
from textwrap import wrap

# HRA Files
from interpreter import prepare_interpreter, runner
from compiler import compiler

if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser(description='CLI for the HRA toolkit')
    required = cli_parser.add_argument_group('required arguments')
    required.add_argument('-f', '--file', type=str, required=True,
                          help='Location of the file')
    required.add_argument('-m', '--memsize', default=32,
                          metavar='SIZE', help='Allocate the size of the memory')

    select = cli_parser.add_argument_group('behaviour arguments')
    select.add_argument('-it', '--interpreter', action='store_true',
                        help='Run the interpreter on given file')
    select.add_argument('-c', '--compiler', action='store_true',
                        help='Run the compiler on given file')

    optional = cli_parser.add_argument_group('optional arguments')
    optional.add_argument('-s', '--state', type=str, choices=['final', 'all', 'none'], default='none',
                          help='Print the type of state of the virtual system')
    optional.add_argument('-i', '--input', type=int, default=[], nargs='+',
                          help='Input for running the file, order of inputs is the same as in memory')
    optional.add_argument('-o', '--output', default=None, type=str,
                          help='Destination file of the assembly')
    optional.add_argument('-r', '--run', action='store_true',
                          help='Run a HRA compiled program')
    optional.add_argument('-va', '--verboseAssembly', action='store_false',
                          help='Gives extra information in the assembly file')

    # Execute the parse_args() method
    args = vars(cli_parser.parse_args())

    if args.get('interpreter') or args.get('compiler'):
        nodes, prepared_system = prepare_interpreter(
            filename=args.get('file'),
            memory_size=args.get('memsize'),
            memory_input=args.get('input')
        )

        # Get interpreter
        if args.get('interpreter'):
            states = runner(nodes, prepared_system)

            # Print state
            if args.get('state') == 'all':
                print(*states, sep='\n')

            elif args.get('state') == 'final':
                *_, final_state = states
                print(final_state)

            print(f'Output: {states[-1].memory[0]}')

        if args.get('compiler'):
            if args.get('output') is None:
                output_filename = args.get('file')
                output_filename = os.path.splitext(output_filename)[0]
            else:
                output_filename = args.get('output')

            compiled_file = compiler(nodes, prepared_system, os.path.split(output_filename)[-1])
            output_filename += '.asm'

            with open(output_filename, 'w') as file:
                file.write(compiled_file)

            print(f'Compiled HRA content to {output_filename}')

            if args.get('run'):
                print(f'Running the compiled program...\n')

                run_filename = output_filename
                base_filename = os.path.splitext(run_filename)[0]
                o_filename = base_filename + '.o'
                elf_filename = base_filename + '.elf'

                o_status = subprocess.run(
                    ['arm-linux-gnueabi-as', run_filename, '-o', o_filename],
                    stdout=subprocess.PIPE
                )
                elf_status = subprocess.run(
                    ['arm-linux-gnueabi-gcc-9', o_filename, '-o', elf_filename, '-nostdlib'],
                    stdout=subprocess.PIPE
                )
                rm_o_status = subprocess.run(
                    ['rm', o_filename],
                    stdout=subprocess.PIPE
                )
                run_status = subprocess.run(
                    ['qemu-arm', f'./{elf_filename}'],
                    stdout=subprocess.PIPE
                )

                output = run_status.stdout
                align = 4
                output_converted = "".join(map(
                    lambda index: str(int.from_bytes(output[index * align:(index + 1) * align], 'little')),
                    range(0, int(len(output) / align))
                ))
                print(output_converted, f'Exited with code: {run_status.returncode}', sep='\n')
