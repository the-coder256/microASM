class T_Token:
    def __init__(self, value): self.value = value
class T_Int:
    def __init__(self, value): self.value = int(value)
class T_Float:
    def __init__(self, value): self.value = float(value)
class T_String:
    def __init__(self, value): self.value = value[1:]
class T_Name:
    def __init__(self, value): self.value = value
class T_Instruction:
    def __init__(self, value): self.value = value
class T_Colon:
    def __init__(self, value): self.value = value
class T_Newline:
    def __init__(self, value): self.value = value
class T_End:
    def __init__(self, value): self.value = value

instructions:list[str] = [
    "nop", "load_value", "load_literal",
    "load_name", "load_label",
    "store_name", "pop_top",
    "call", "bin_op",
    "jump_label", "jump_if_false",
    "jump_if_true", "return_value",
    "return_const", "delete_name",
    "bin_index", "make_list",
    "make_tuple", "make_dict"
]

class Tokeniser:
    def __init__(self):
        self.content:str = ""
        self.tokens:list = []
        self.curr_tok:str = ""

    def create_token(self, value:str)->T_Token:
        t_type = T_Token
        if value == ":":
            t_type = T_Colon
        elif value == "\n":
            t_type = T_Newline
        elif value[0] in ["'", '"']:
            t_type = T_String
        elif value in instructions:
            t_type = T_Instruction
        else:
            try:
                x = float(value)
                del x
                if value.count(".") == 0:
                    t_type = T_Int
                else:
                    t_type = T_Float
            except ValueError:
                t_type = T_Name
        return t_type(value)

    def append_token(self, extra=None)->None:
        if self.curr_tok:
            self.tokens.append(self.create_token(self.curr_tok))
            self.curr_tok = ""
        if extra:
            self.tokens.append(self.create_token(extra))

    def tokenise(self, content:str)->list[T_Token]:
        self.content:str = content
        self.tokens:list = []
        self.curr_tok:str = ""
        in_string = 0
        string_char = ""
        in_comment = 0
        for index in range(len(content)):
            char = content[index]
            if char == "\n":
                self.append_token("\n")
                in_comment = 0
            elif char == ";":
                in_comment = 1
            elif in_comment:
                continue
            elif char in ["'", '"'] and not in_string:
                self.curr_tok += char
                in_string = 1
                string_char = char
            elif char == string_char and in_string:
                in_string = 0
            elif in_string:
                self.curr_tok += char
            elif char == " ":
                self.append_token()
            elif char == ":":
                self.append_token(":")
            else:
                self.curr_tok += char
        self.append_token()
        self.tokens.append(T_End("END"))
        return self.tokens