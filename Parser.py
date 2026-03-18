class Parser:
    def __init__(self, tokens, sym_table):
        self.tokens = tokens
        self.pos = 0
        self.sym_table = sym_table

    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def advance(self):
        self.pos += 1

    def match(self, token_type):
        token = self.current()

        if token and token.type == token_type:
            self.advance()
            return token

        # Still needs to change this error handling
        raise SyntaxError(
            f"Esperado {token_type}, encontrado {token.type if token else 'EOF'}"
        )
    

    
    def programa(self):
        self.match("programa")

        name = self.match("identificador")

        self.sym_table.insert(name=name.lexeme, type="nome_programa", category="variável")

        self.match("ponto_virgula")

        self.bloco()

        self.match("ponto")



    def bloco(self):
        if self.current() and self.current().type == "variavel":
            self.parte_declaracao_variaveis()

        if self.current() and self.current().type == "procedimento":
            self.parte_declaracao_sub_rotinas()

        self.comando_composto()




    def parte_declaracao_variaveis(self):
        self.match("variavel")

        self.declaracao_variaveis()

        while self.current() and self.current().type == "ponto_virgula":

            self.match("ponto_virgula")

            if self.current() and self.current().type == "identificador":
                self.declaracao_variaveis()

    def declaracao_variaveis(self):
        tipo = self.match("identificador")

        ids = self.lista_identificadores()

        for ident in ids:
            # Still needs to change this error handling
            if self.sym_table.lookup(ident.lexeme):
                raise Exception(f"Variável {ident.lexeme} já declarada")

            self.sym_table.insert(name=ident.lexeme, type=tipo.lexeme, category="variable")

    def lista_identificadores(self):
        ids = []

        ids.append(self.match("identificador"))

        while self.current() and self.current().type == "virgula":
            self.match("virgula")

            ids.append(self.match("identificador"))

        return ids
    


    def parte_declaracao_sub_rotinas(self):
        
        