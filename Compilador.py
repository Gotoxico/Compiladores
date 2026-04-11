import Lexer, Symbol_table, Parser

class Compilador:
    def __init__(self):
        self.lexer = Lexer.lexer()
        self.sym_table = Symbol_table.SymbolTable()
        self.tokens = []
        self.pos = 0
        self.errors = []


    def compile(self, source_code):
        self.tokens = list(self.lexer.analise(source_code))

        parser = Parser.Parser(self.tokens, self.sym_table, self.errors)
        
        TreeNode = parser.programa()

        return self.sym_table, self.errors, TreeNode


    
    