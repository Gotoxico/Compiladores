import Lexer, Symbol_table, Parser

class Compilador:
    def __init__(self):
        self.lexer = Lexer.lexer()
        self.sym_table = Symbol_table.SymbolTable()
        self.tokens = []
        self.pos = 0

    def compile(self, source_code):
        self.tokens = list(self.lexer.analise(source_code))

        parser = Parser.Parser(self.tokens, self.sym_table)
        
        parser.programa()

        return self.sym_table


    
    