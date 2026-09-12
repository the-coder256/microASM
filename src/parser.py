import tokeniser

class Node: pass
class Instruction:
    def __init__(self, instruction:str, argument=None): self.instruction, self.argument = instruction, argument
class Label:
    def __init__(self, name:str): self.name = name
class Name:
    def __init__(self, name:str): self.name = name

class Parser:
    def __init__(self):
        self.tokens = []
        self.tree = []
        self.index = 0

    def peek(self, amount:int = 1)->tokeniser.T_Token:
        try:
            return self.tokens[self.index + amount]
        except IndexError:
            return tokeniser.T_End("END")

    def consume(self)->tokeniser.T_Token:
        try:
            return self.tokens[self.index]
        except IndexError:
            return tokeniser.T_End("END")

    def advance(self)->tokeniser.T_Token:
        value = self.consume()
        self.index += 1
        return value

    def at_end(self)->bool:
        return type(self.consume()) == tokeniser.T_End

    def parse_expr(self):
        start = self.advance()
        if type(start) == tokeniser.T_Name:
            return Name(start.value)
        else:
            return start.value

    def parse_instruction(self)->Instruction:
        instruction:str = self.peek(-1).value
        if type(self.consume()) in [tokeniser.T_Newline, tokeniser.T_End]:
            # no argument
            argument = None
        else:
            # yes argument
            argument = self.parse_expr()
        self.advance()
        return Instruction(instruction, argument)

    def parse_label(self)->Label:
        label_name = self.peek(-1).value
        # WE already know theres a : following the name so ye
        self.advance()    # from : -> \n
        self.advance()    # from \n -> some bs idk
        return Label(label_name)
    
    def parse_stmt(self)->Node:
        start = self.advance()
        if type(start) == tokeniser.T_Instruction:
            return self.parse_instruction()
        elif type(self.consume()) == tokeniser.T_Colon:
            return self.parse_label()

    def parse(self, tokens:list[tokeniser.T_Token])->list[Node]:
        self.tokens = tokens
        self.tree = []
        self.index = 0
        while not self.at_end():
            node = self.parse_stmt()
            self.tree.append(node)
        return self.tree