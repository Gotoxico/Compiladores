import Tree

class Parser:
    def __init__(self, tokens, sym_table, errors):
        self.tokens = tokens
        self.pos = 0
        self.sym_table = sym_table
        self.errors = errors

    def error(self, message):
        token = self.current()
        self.errors.append({
            "message": message,
            "line": token.line if token else None,
            "col": token.col_start if token else None
        })

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

        self.error(f"Esperado token do tipo {token_type}, mas encontrado {token.type if token else 'EOF'}")
        self.advance()  
        return None
    
    def match_node(self, token_type, flag_return_token=False):
        token = self.match(token_type)
        if token:
            if flag_return_token:
                return token, Tree.TreeNode(type=token.type, value=token.lexeme)
            else:
                return Tree.TreeNode(type=token.type, value=token.lexeme)
        else:
            if flag_return_token:
                return None, Tree.TreeNode('<ERROR>', f'Token do tipo {token_type} esperado, mas encontrado {token.type if token else "EOF"}')
            else:
                return Tree.TreeNode('<ERROR>', f'Token do tipo {token_type} esperado, mas encontrado {token.type if token else "EOF"}')        

    
    
    def programa(self):

        program_node = Tree.TreeNode(type="<programa>")
        program_node.add_child(self.match_node("programa"))


        name = self.match("identificador")

        if name:
            self.sym_table.insert(name=name.lexeme, type="nome_programa", category="variável")
            program_node.add_child(Tree.TreeNode(type="Terminal", value=name.lexeme))

        program_node.add_child(self.match_node("ponto_virgula"))

        program_node.add_child(self.bloco())

        program_node.add_child(self.match_node("ponto"))

        return program_node

    def bloco(self):
        block_node = Tree.TreeNode(type="<bloco>")
        if self.current() and self.current().type == "identificador_tipo":
            block_node.add_child(self.parte_declaracao_variaveis())

        if self.current() and self.current().type == "procedimento":
            block_node.add_child(self.parte_declaracao_sub_rotinas())

        block_node.add_child(self.comando_composto())
        return block_node

    def parte_declaracao_variaveis(self):
        variable_declaration_part_node = Tree.TreeNode(type="<parte_declaracao_variaveis>")
        variable_declaration_part_node.add_child(self.declaracao_variaveis())

        while self.current() and self.current().type == "ponto_virgula":
            variable_declaration_part_node.add_child(self.match_node("ponto_virgula"))

            if self.current() and self.current().type == "identificador_tipo":
                variable_declaration_part_node.add_child(self.declaracao_variaveis())
        return variable_declaration_part_node

    def declaracao_variaveis(self):
        variable_declaration_node = Tree.TreeNode(type="<declaracao_variaveis>")
        tipo = self.match("identificador_tipo")

        if tipo:
            variable_declaration_node.add_child(self.tipo(tipo))
        
        identifiers, variable_list_node = self.lista_identificadores()
        variable_declaration_node.add_child(variable_list_node)
        self.fill_table(identifiers, tipo, "variável")

        return variable_declaration_node
    
    def tipo(self, tipo):
        type_node = Tree.TreeNode(type="<tipo>")
        type_node.add_child(Tree.TreeNode(type="Terminal", value=tipo.lexeme))
        return type_node

    def lista_identificadores(self ):
        variable_list_node = Tree.TreeNode(type="<lista_identificadores>")  
        ids = []
        token, variable_child = self.match_node("identificador", flag_return_token=True)

        ids.append(token)
        variable_list_node.add_child(variable_child)

        while self.current() and self.current().type == "virgula":
            variable_list_node.add_child(self.match_node("virgula"))

            token, variable_child = self.match_node("identificador", flag_return_token=True)
            ids.append(token)
            variable_list_node.add_child(variable_child)

        return ids, variable_list_node
    
    def fill_table(self, identifiers, type, category):
        for ident in identifiers:
            # We still need to change this error handling
            if self.sym_table.lookup_current_scope(ident.lexeme):
                error_message = f"{category.capitalize()} {ident.lexeme} já existe no escopo atual"
                self.error(error_message)

            self.sym_table.insert(name=ident.lexeme, type=type.lexeme, category=category)

    def parte_declaracao_sub_rotinas(self):
        subroutine_declaration_part_node = Tree.TreeNode(type="<parte_declaracao_sub_rotinas>")
        subroutine_declaration_part_node.add_child(self.declaracao_procedimento())

        while self.current() and self.current().type == "ponto_virgula":
            subroutine_declaration_part_node.add_child(self.match_node("ponto_virgula"))

            if self.current() and self.current().type == "procedimento":
                subroutine_declaration_part_node.add_child(self.declaracao_procedimento())

        return subroutine_declaration_part_node


    def declaracao_procedimento(self):
        subroutine_declaration_node = Tree.TreeNode(type="<declaracao_procedimento>")
        subroutine_declaration_node.add_child(self.match_node("procedimento"))
        identificador = self.match("identificador")

        if identificador:
            if self.sym_table.lookup_current_scope(identificador.lexeme) :
                error_message = f"Procedimento {identificador.lexeme} já declarado"
                self.error(error_message)
                subroutine_declaration_node.add_child(Tree.TreeNode('<ERROR>', error_message))
            else:  
                subroutine_declaration_node.add_child(Tree.TreeNode(type="Terminal", value=identificador.lexeme)) 


        self.sym_table.insert(
            name=identificador.lexeme,
            type= 'procedure',
            category="procedimento"
        )

        self.sym_table.enter_scope(identificador.lexeme)

        if self.current() and self.current().type == "abre_parentese":
            subroutine_declaration_node.add_child(self.parametros_formais())

        subroutine_declaration_node.add_child(self.match_node("ponto_virgula"))

        subroutine_declaration_node.add_child(self.bloco())
        self.sym_table.exit_scope()

        return subroutine_declaration_node

    def parametros_formais(self):
        formal_parameters_node = Tree.TreeNode(type="<parametros_formais>")
        formal_parameters_node.add_child(self.match_node("abre_parentese"))

        formal_parameters_node.add_child(self.secao_parametros_formais())

        while self.current() and self.current().type == "ponto_virgula":
            formal_parameters_node.add_child(self.match_node("ponto_virgula"))
            formal_parameters_node.add_child(self.secao_parametros_formais())

        formal_parameters_node.add_child(self.match_node("fecha_parentese"))
        return formal_parameters_node
    

    def secao_parametros_formais(self):
        formal_parameter_section_node = Tree.TreeNode(type="<secao_parametros_formais>")

        if self.current().type == "variavel":
            formal_parameter_section_node.add_child(self.match_node("variavel"))

        identifiers, variable_list_node = self.lista_identificadores()
        formal_parameter_section_node.add_child(variable_list_node)
    

        formal_parameter_section_node.add_child(self.match_node("dois_pontos"))

        identificador_tipo, child = self.match_node("identificador_tipo", flag_return_token=True)
        formal_parameter_section_node.add_child(child)

        self.fill_table(identifiers, identificador_tipo, "variável")

        return formal_parameter_section_node


    def comando_composto(self):
        compound_command_node = Tree.TreeNode(type="<comando_composto>")
        compound_command_node.add_child(self.match_node("begin"))

        if self.current() and self.current().type != "end":
            compound_command_node.add_child(self.comando())

            while self.current() and self.current().type == "ponto_virgula":
                compound_command_node.add_child(self.match_node("ponto_virgula"))
                compound_command_node.add_child(self.comando())
        compound_command_node.add_child(self.match_node("end"))
        return compound_command_node
    
    def comando(self):
        command_node = Tree.TreeNode(type="<comando>")
        token = self.current()

        if not token:
            return 
        
        if token.type == "end":
            return

        if token.type in ("identificador", "identificador_procedimento"):
            ident, child = self.match_node(token.type, flag_return_token=True)
            command_node.add_child(child)
            command_node.add_child(self.resto_identificador(ident))
        elif token.type == "if":
            command_node.add_child(self.comando_condicional())
        elif token.type == "while":
            command_node.add_child(self.comando_repetitivo())
        elif token.type == "begin":
            command_node.add_child(self.comando_composto())
        else:
            self.error(f"Comando inesperado: {token.lexeme} Linha: {token.line}")
            self.advance() 
            command_node.add_child(Tree.TreeNode('<ERROR>', f"Comando inesperado: {token.lexeme} Linha: {token.line}"))
        
        return command_node

    def resto_identificador(self, ident):
        ident_rest_node = Tree.TreeNode(type="<resto_identificador>")
        token = self.current()

        if token and token.type == "abre_colchete":
            ident_rest_node.add_child(self.match_node("abre_colchete"))
            
            ident_rest_node.add_child(self.expressao())
            ident_rest_node.add_child(self.match_node("fecha_colchete"))
            token = self.current() 

        if token and token.type == "atribuicao":
            self.sym_table.add_reference(ident.lexeme)
            ident_rest_node.add_child(self.match_node("atribuicao"))
            ident_rest_node.add_child(self.expressao())

        elif token and token.type == "abre_parentese":
            self.sym_table.add_reference(ident.lexeme)
            ident_rest_node.add_child(self.match_node("abre_parentese"))
            if self.current() and self.current().type != "fecha_parentese":
                ident_rest_node.add_child(self.lista_expressoes())
            ident_rest_node.add_child(self.match_node("fecha_parentese"))
            
        else:
            self.sym_table.add_reference(ident.lexeme)
            ident_rest_node.add_child(Tree.TreeNode(type="Terminal", value=ident.lexeme))
        
        return ident_rest_node

    def comando_condicional(self):
        conditional_command_node = Tree.TreeNode(type="<comando_condicional>")
        conditional_command_node.add_child(self.match_node("if"))
        conditional_command_node.add_child(self.expressao())
        conditional_command_node.add_child(self.match_node("then"))

        conditional_command_node.add_child(self.comando())

        if self.current() and self.current().type == "else":
            conditional_command_node.add_child(self.match_node("else"))
            conditional_command_node.add_child(self.comando())

        return conditional_command_node

    def comando_repetitivo(self):
        repetitive_command_node = Tree.TreeNode(type="<comando_repetitivo>")
        repetitive_command_node.add_child(self.match_node("while"))
        repetitive_command_node.add_child(self.expressao())
        repetitive_command_node.add_child(self.match_node("do"))
        repetitive_command_node.add_child(self.comando())
        return repetitive_command_node


    def lista_expressoes(self):
        expression_list_node = Tree.TreeNode(type="<lista_expressoes>")
        expression_list_node.add_child(self.expressao())

        while self.current() and self.current().type == "virgula":
            expression_list_node.add_child(self.match_node("virgula"))
            expression_list_node.add_child(self.expressao())

        return expression_list_node

    def expressao(self):
        expression_node = Tree.TreeNode(type="<expressao>")
        expression_node.add_child(self.expressao_simples())

        if self.current() and self.current().type == "relacao":
            expression_node.add_child(self.match_node("relacao"))
            expression_node.add_child(self.expressao_simples())
        
        return expression_node

    def expressao_simples(self):
        # Lida com o [+|-] opcional no início (Regra 18) 
        simple_expression_node = Tree.TreeNode(type="<expressao_simples>")

        if self.current() and self.current().type in ("operador_soma", "operador_subtracao"):
            simple_expression_node.add_child(self.match_node(self.current().type))
            # self.advance()

        simple_expression_node.add_child(self.termo())

        while self.current() and self.current().type in ("operador_soma", "operador_subtracao", "or"):
            simple_expression_node.add_child(self.match_node(self.current().type))
            # self.advance()
            simple_expression_node.add_child(self.termo())

        return simple_expression_node

    def termo(self):
        term_node = Tree.TreeNode(type="<termo>")
        term_node.add_child(self.fator())

        while self.current() and self.current().type in ("operador_multiplicacao", "operador_divisao", "and"):
            term_node.add_child(self.match_node(self.current().type))
            # self.advance()
            term_node.add_child(self.fator())
        
        return term_node
    
    def fator(self):
        factor_node = Tree.TreeNode(type="<fator>")
        token = self.current()

        if not token:
            self.error("Fim de arquivo inesperado")
            return
        
        if token.type == "numero_inteiro":
            factor_node.add_child(self.match_node("numero_inteiro"))

        elif token.type == "identificador_constante":
            factor_node.add_child(self.match_node("identificador_constante"))
        
        elif token.type == "identificador":
            ident = self.match("identificador")
            self.sym_table.add_reference(ident.lexeme)
            factor_node.add_child(Tree.TreeNode(type="Terminal", value=ident.lexeme))
            
            if self.current() and self.current().type == "abre_colchete":
                factor_node.add_child(self.match_node("abre_colchete"))
                factor_node.add_child(self.expressao())
                factor_node.add_child(self.match_node("fecha_colchete"))

        elif token.type == "abre_parentese":
            factor_node.add_child(self.match_node("abre_parentese"))
            factor_node.add_child(self.expressao())
            factor_node.add_child(self.match_node("fecha_parentese"))
        
        elif token.type == "not":
            factor_node.add_child(self.match_node("not"))
            factor_node.add_child(self.fator())

        else:
            self.error(f"Fator inesperado: {token.lexeme} Linha: {token.line}")
            factor_node.add_child(Tree.TreeNode('<ERROR>', f"Fator inesperado: {token.lexeme} Linha: {token.line}"))
            self.advance()
        
        return factor_node