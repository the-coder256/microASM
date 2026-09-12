from sys import argv
import tokeniser
import parser
import generator

if len(argv) < 2:
    print("error: no input files")
    exit(1)

with open(argv[1], "r") as file:
    content = file.read()

tokens = tokeniser.Tokeniser().tokenise(content)
tree = parser.Parser().parse(tokens)
bytecode = generator.Generator().generate(tree)

with open("output.bin", "wb") as file:
    file.write(bytecode)