import parser

class Generator:
    def __init__(self):
        self.bytecode = bytearray()
        self.tree = []
        self.labels = {}
        self.empty_addresses = []    # every entry: (address_to_be_filled, label_to_get_address_from)
        self.names = []
        self.constants = [0]
        self.bp = 0    # for writing to bytearray

    def write(self, byte:int, loc:int)->None:
        try:
            self.bytecode[loc] = byte
        except IndexError:
            pass

    def append(self, byte:int)->None:
        self.bytecode.append(byte)
        self.bp += 1

    def generate_number(self, num:int)->None:
        self.append(int(num % 256))
        self.append(int((num / 256) % 256))

    def generate_from_op(self, op)->None:
        if type(op) == int:
            self.generate_number(op)
        else:    # literal +, -, * etc
            if type(op) == parser.Name:
                name = op.name
            else:
                name = op
            if   name == "+":  self.generate_number(0)
            elif name == "-":  self.generate_number(1)
            elif name == "*":  self.generate_number(2)
            elif name == "/":  self.generate_number(3)
            elif name == "==": self.generate_number(4)
            elif name == "<":  self.generate_number(5)
            elif name == ">":  self.generate_number(6)
            elif name == "<=": self.generate_number(7)
            elif name == ">=": self.generate_number(8)
            elif name == "&&": self.generate_number(9)
            elif name == "||": self.generate_number(10)
            elif name == "!":  self.generate_number(11)
            elif name == "&":  self.generate_number(12)
            elif name == "|":  self.generate_number(13)
            elif name == "~":  self.generate_number(14)
            elif name == "^":  self.generate_number(15)
            elif name == "<<": self.generate_number(16)
            elif name == ">>": self.generate_number(17)

    def generate_from_expr(self, expr)->None:
        # theres a possible optimisation below me but it saves only like 6 lines so it isnt worth it
        if type(expr) == int:
            if (0x1a, expr) not in self.constants:
                number = len(self.constants)
                self.constants.append((0x1a, expr))
            else:
                number = self.constants.index((0x1a, expr))
            self.append(number % 256)
            self.append(int(number / 256))
        elif type(expr) == float:
            if (0x1a, expr) not in self.constants:
                number = len(self.constants)
                self.constants.append((0x1a, expr))
            else:
                number = self.constants.index((0x1a, expr))
            self.append(number % 256)
            self.append(int(number / 256))
        elif type(expr) == str:
            if (0x1f, expr) not in self.constants:
                number = len(self.constants)
                self.constants.append((0x1f, expr))
            else:
                number = self.constants.index((0x1f, expr))
            self.append(number % 256)
            self.append(int(number / 256))
        elif type(expr) == parser.Name:
            name = expr.name
            if name not in self.names:
                number = len(self.names)
                self.names.append(name)
            else:
                number = self.names.index(name)
            self.append(number % 256)
            self.append(int(number / 256))

    def generate_from_node(self, node:parser.Node)->None:
        if type(node) == parser.Instruction:
            instruction:str = node.instruction
            if instruction == "nop":
                self.append(0x1c)
            elif instruction == "load_value":
                self.append(0x20)
                self.generate_from_expr(node.argument)
            elif instruction == "load_literal":
                self.append(0x2a)
                self.generate_number(node.argument)
            elif instruction == "load_name":
                self.append(0x30)
                self.generate_from_expr(node.argument)
            elif instruction == "load_label":
                self.append(0x2a)
                self.empty_addresses.append((self.bp, node.argument))
                self.generate_number(0)
            elif instruction == "store_name":
                self.append(0x3f)
                self.generate_from_expr(node.argument)
            elif instruction == "pop_top":
                self.append(0x40)
            elif instruction == "call":
                self.append(0x4a)
                self.generate_number(node.argument)
            elif instruction == "bin_op":
                self.append(0x50)
                self.generate_from_op(node.argument)
            elif instruction == "jump_label":
                self.append(0x60)
                self.empty_addresses.append((self.bp, node.argument))
                self.generate_number(0)
            elif instruction == "jump_if_false":
                self.append(0x6a)
                self.empty_addresses.append((self.bp, node.argument))
                self.generate_number(0)
            elif instruction == "jump_if_true":
                self.append(0x60)
                self.empty_addresses.append((self.bp, node.argument))
                self.generate_number(0)
            elif instruction == "return_value":
                self.append(0x70)
            elif instruction == "return_const":
                self.append(0x77)
                self.generate_from_expr(node.argument)
        elif type(node) == parser.Label:
            self.labels.update({node.name: self.bp})

    def generate(self, tree:list[parser.Node])->bytearray:
        self.bytecode = bytearray()
        self.tree = tree
        self.labels = {}
        self.empty_addresses = []
        self.names = []
        self.constants = [0]
        self.bp = 0
        final_bytecode = bytearray()
        # magic bytes
        final_bytecode.append(0xa0)
        final_bytecode.append(0xff)
        # generation retro 1
        # generates instructions and collects names, constants, and labels
        for node in tree:
            self.generate_from_node(node)
        # generation round 2
        # resolves empty addresses and generates (and combines) bytecode for constants, names and instructions
        # 2-1: resolve empty addresses
        for to_resolve in self.empty_addresses:
            address = to_resolve[0]
            label = to_resolve[1]
            if type(label) == parser.Name:
                name = label.name
            else:
                name = label
            label_loc:int = self.labels.get(name)
            self.write(label_loc % 256, address)
            self.write(int(label_loc / 256) % 256, address + 1)
        # 2-2: generate bytecode for constants and names
        # constants
        for const in self.constants[1:]:
            const_type:int = const[0]
            const_value:str = str(const[1])
            if const_type not in [0x1a, 0x1f]:
                print("error: unsupported constant type")
                exit(1)
            final_bytecode.append(const_type)
            for char in const_value:
                final_bytecode.append(ord(char))
            final_bytecode.append(0x00)
        final_bytecode.append(0xff)
        # names
        for name in self.names:
            for char in name:
                final_bytecode.append(ord(char))
            final_bytecode.append(0x00)
        final_bytecode.append(0xff)
        # 2-3: write instructions to final bytecode
        for byte in self.bytecode:
            final_bytecode.append(byte)
        final_bytecode.append(0xff)
        return final_bytecode