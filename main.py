from interpreter.lexer import lexer
from interpreter.parser import parser, parseNodes
from interpreter.runner import runner
from interpreter.system import system


with open('programs/test.hra', 'r') as f:
    lexed = lexer(f.read())


parsed = parseNodes(parser(lexed))
runner(parsed, system(20))


