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
            f"Esperado {token_type}, encontrado {token.type if token else 'EOF'} Linha: {token.line}"
        )
    

    
    def programa(self):
        self.match("programa")

        name = self.match("identificador")

        self.sym_table.insert(name=name.lexeme, type="nome_programa", category="variável")

        self.match("ponto_virgula")

        self.bloco()

        self.match("ponto")



    def bloco(self):
        if self.current() and self.current().type == "identificador_tipo":
            self.parte_declaracao_variaveis()

        if self.current() and self.current().type == "procedimento":
            self.parte_declaracao_sub_rotinas()

        self.comando_composto()




    def parte_declaracao_variaveis(self):
        self.declaracao_variaveis()

        while self.current() and self.current().type == "ponto_virgula":
            self.match("ponto_virgula")

            if self.current() and self.current().type == "identificador_tipo":
                self.declaracao_variaveis()

    def declaracao_variaveis(self):
        tipo = self.match("identificador_tipo")

        ids = self.lista_identificadores()

        for ident in ids:
            # We still need to change this error handling
            if self.sym_table.lookup_current_scope(ident.lexeme):
                raise Exception(f"Variável {ident.lexeme} já declarada")

            self.sym_table.insert(name=ident.lexeme, type=tipo.lexeme, category="variável")

    def lista_identificadores(self):
        ids = []

        ids.append(self.match("identificador"))

        while self.current() and self.current().type == "virgula":
            self.match("virgula")

            ids.append(self.match("identificador"))

        return ids
    


    def parte_declaracao_sub_rotinas(self):
        self.declaracao_procedimento()

        while self.current() and self.current().type == "ponto_virgula":
            self.match("ponto_virgula")

            if self.current() and self.current().type == "procedimento":
                self.declaracao_procedimento()

    def declaracao_procedimento(self):
        tipo = self.match("procedimento")
        identificador = self.match("identificador")

        if self.sym_table.lookup_current_scope(identificador.lexeme):
            raise Exception(f"Procedimento {identificador.lexeme} já declarado")

        self.sym_table.insert(
            name=identificador.lexeme,
            type=tipo.lexeme,
            category="procedimento"
        )

        self.sym_table.enter_scope(identificador.lexeme)

        if self.current() and self.current().type == "abre_parentese":
            self.parametros_formais()

        self.match("ponto_virgula")

        self.bloco()

        self.sym_table.exit_scope()

    def parametros_formais(self):
        self.match("abre_parentese")

        self.secao_parametros_formais()

        while self.current() and self.current().type == "ponto_virgula":
            self.match("ponto_virgula")

            self.secao_parametros_formais()

        self.match("fecha_parentese")

    def secao_parametros_formais(self):
        if self.current().type == "variavel":
            self.match("variavel")

        identificadores = self.lista_identificadores()

        self.match("dois_pontos")

        identificador_tipo = self.match("identificador_tipo")

        for ident in identificadores:
            # We still need to change this error handling
            if self.sym_table.lookup_current_scope(ident.lexeme):
                raise Exception(f"Parâmetro formal {ident.lexeme} já declarado")

            self.sym_table.insert(name=ident.lexeme, type=identificador_tipo.lexeme, category="parâmetro-formal", passed_as="valor")

    def comando_composto(self):
        self.match("begin")

        if self.current() and self.current().type != "end":
            self.comando()
            while self.current() and self.current().type == "ponto_virgula":
                self.match("ponto_virgula")
                self.comando()
        self.match("end")
    
    def comando(self):
        token = self.current()

        # These two initial ifs are more of a precaution against case that was bugging without the first two optional parts of a program
        if not token:
            return
        
        if token.type == "end":
            return

        if token.type in ("identificador", "identificador_procedimento"):
            ident = self.match(token.type)
            self.resto_identificador(ident)
        elif token.type == "if":
            self.comando_condicional()
        elif token.type == "while":
            self.comando_repetitivo()
        elif token.type == "begin":
            self.comando_composto()
        else:
            raise SyntaxError(f"Comando inesperado: {token.lexeme}")

    def resto_identificador(self, ident):
        token = self.current()

        if token and token.type == "atribuicao":
            self.sym_table.add_reference(ident.lexeme)
            self.match("atribuicao")
            self.expressao()

        elif token and token.type == "abre_parentese":
            self.sym_table.add_reference(ident.lexeme)
            self.match("abre_parentese")

            if self.current() and self.current().type != "fecha_parentese":
                self.lista_expressoes()

            self.match("fecha_parentese")
        else:
            pass  # Ainda precisa melhorar esse tratamento de erro

    def comando_condicional(self):
        self.match("if")
        self.expressao()
        self.match("then")

        self.comando()

        if self.current() and self.current().type == "else":
            self.match("else")
            self.comando()

    def comando_repetitivo(self):
        self.match("while")
        self.expressao()
        self.match("do")
        self.comando()

    def lista_expressoes(self):
        self.expressao()

        while self.current() and self.current().type == "virgula":
            self.match("virgula")
            self.expressao()

    def expressao(self):
        self.expressao_simples()

        if self.current() and self.current().type == "relacao":
            self.match("relacao")
            self.expressao_simples()

    def expressao_simples(self):
        self.termo()

        while self.current() and self.current().type in ("operador_soma", "operador_subtracao", "or"):
            self.advance()
            self.termo()

    def termo(self):
        self.fator()

        while self.current() and self.current().type in ("operador_multiplicacao", "operador_divisao", "and"):
            self.advance()
            self.fator()
    
    def fator(self):
        token = self.current()

        if not token:
            raise SyntaxError("Fim de arquivo inesperado")
        
        if token.type == "numero_inteiro":
            self.match("numero_inteiro")

        elif token.type == "identificador_constante":
            const = self.match("identificador_constante")
            '''self.sym_table.add_reference(const.lexeme)'''
        
        elif token.type == "identificador":
            ident = self.match("identificador")
            self.sym_table.add_reference(ident.lexeme)
            self.resto_identificador(ident)

        elif token.type == "abre_parentese":
            self.match("abre_parentese")
            self.expressao()
            self.match("fecha_parentese")
        
        elif token.type == "not":
            self.match("not")
            self.fator()

        else:
            raise SyntaxError(f"Fator inesperado: {token.lexeme} Linha: {token.line}")