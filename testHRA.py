from typing import List
from subprocess import run, PIPE


class col:
    OK = '\033[92m'
    FAIL = '\033[91m'
    RESET = '\033[0m'


def testHRAFile(filename: str, expected_output: str, expected_input: List[str] = ' '):
    """
    Test the given filename with the expected input and output
    :param filename: Filename which will be tested
    :param expected_output: Expected output
    :param expected_input: Expected Input
    """
    print(f'{",".join(expected_input)}'.ljust(5), expected_output.ljust(20), f"{filename}".ljust(40), end='')
    if expected_input == ' ':
        expected_input = ['0']

    it_status = run(
        ['python3', 'hra-toolkit.py', '-f', filename, '-it', '-so', '-i', *expected_input],
        stdout=PIPE
    )
    status = it_status.stdout.decode('ascii')[:-1]
    print(f'{col.FAIL}x' if status != expected_output else f'{col.OK}o', end=f'{col.RESET} ')

    cp_status = run(
        ['python3', 'hra-toolkit.py', '-f', filename, '-cr', '-so', '-i', *expected_input],
        stdout=PIPE
    )
    status = cp_status.stdout.decode('ascii')[:-1]
    print(f'{col.FAIL}x' if status != expected_output else f'{col.OK}o', end=f'{col.RESET} ')

    if it_status.returncode:
        if cp_status.returncode:
            print('Interpreter and Compiler failed!')
        print('Interpreter failed!')
    elif cp_status.returncode:
        print('Compiler failed!')
    else:
        print('Finished tests successfully!')


if __name__ == '__main__':
    print(f'In'.ljust(6), 'Out'.ljust(21), 'Filename'.ljust(40), 'I ', 'C ', 'Verdict', sep='')
    testHRAFile('programs/test_recursion.hra', '012345678910')
    testHRAFile('programs/test_recursion.hra', '5678910', ['5'])
    testHRAFile('programs/test_recursion.hra', '910', ['9'])
    testHRAFile('programs/sommig.hra', '0', ['0'])
    testHRAFile('programs/sommig.hra', '1', ['1'])
    testHRAFile('programs/sommig.hra', '2', ['2'])
    testHRAFile('programs/sommig.hra', '3', ['3'])
    testHRAFile('programs/is_even.hra', '1', ['0'])
    testHRAFile('programs/is_even.hra', '0', ['1'])
    testHRAFile('programs/is_even.hra', '1', ['2'])
    testHRAFile('programs/is_even.hra', '0', ['3'])


