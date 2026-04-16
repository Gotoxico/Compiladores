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

    def sync(self, sync_symbols):
        while self.current() is not None:
            if self.current().type in sync_symbols:
                return
            
            self.advance()

    def match(self, token_type, sync_symbols):
        token = self.current()

        if token and token.type == token_type:
            self.advance()
            return token

        self.error(f"Esperado token do tipo {token_type}, mas encontrado {token.type if token else 'EOF'}")
        self.sync(sync_symbols)
        return None
    
    def match_node(self, token_type, sync_symbols, flag_return_token=False):
        token = self.match(token_type, sync_symbols)
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
            
    def fill_table(self, identifiers, type, category):
        for ident in identifiers:
            # We still need to change this error handling
            if self.sym_table.lookup_current_scope(ident.lexeme):
                error_message = f"{category.capitalize()} {ident.lexeme} já existe no escopo atual"
                self.error(error_message)

            self.sym_table.insert(name=ident.lexeme, type=type.lexeme, category=category)
    

    
    def programa(self):
        program_node = Tree.TreeNode(type="<programa>")
        program_node.add_child(self.match_node("programa", {"identificador", "ponto_virgula", "identificador_tipo", "procedimento", "begin", "ponto"}))

        name = self.match("identificador", {"ponto_virgula", "identificador_tipo", "procedimento", "begin", "ponto"})

        if name:
            self.sym_table.insert(name=name.lexeme, type="nome_programa", category="variável")
            program_node.add_child(Tree.TreeNode(type="Terminal", value=name.lexeme))

        program_node.add_child(self.match_node("ponto_virgula", {"identificador_tipo", "procedimento", "begin", "ponto"}))

        program_node.add_child(self.bloco())

        program_node.add_child(self.match_node("ponto", {}))

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
            variable_declaration_part_node.add_child(self.match_node("ponto_virgula", {"identificador_tipo", "procedimento", "begin"}))

            if self.current() and self.current().type == "identificador_tipo":
                variable_declaration_part_node.add_child(self.declaracao_variaveis())
        return variable_declaration_part_node

    def declaracao_variaveis(self):
        variable_declaration_node = Tree.TreeNode(type="<declaracao_variaveis>")
        tipo = self.match("identificador_tipo", {"identificador", "ponto_virgula"})

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
        sync_set = {"virgula", "dois_pontos", "ponto_virgula"}

        token, variable_child = self.match_node("identificador", sync_set, flag_return_token=True)

        if token: 
            ids.append(token)
        variable_list_node.add_child(variable_child)

        while self.current() and self.current().type == "virgula":
            variable_list_node.add_child(self.match_node("virgula", sync_set))

            token, variable_child = self.match_node("identificador", sync_set, flag_return_token=True)
            if token:
                ids.append(token)
            variable_list_node.add_child(variable_child)

        return ids, variable_list_node
    
    

    def parte_declaracao_sub_rotinas(self):
        subroutine_declaration_part_node = Tree.TreeNode(type="<parte_declaracao_sub_rotinas>")
        subroutine_declaration_part_node.add_child(self.declaracao_procedimento())

        while self.current() and self.current().type == "ponto_virgula":
            subroutine_declaration_part_node.add_child(self.match_node("ponto_virgula", {"procedimento", "begin"}))

            if self.current() and self.current().type == "procedimento":
                subroutine_declaration_part_node.add_child(self.declaracao_procedimento())

        return subroutine_declaration_part_node


    def declaracao_procedimento(self):
        subroutine_declaration_node = Tree.TreeNode(type="<declaracao_procedimento>")
        subroutine_declaration_node.add_child(self.match_node("procedimento", {"identificador", "abre_parentese", "ponto_virgula"}))
        identificador = self.match("identificador", {"abre_parentese", "ponto_virgula"})

        if identificador:
            if self.sym_table.lookup_current_scope(identificador.lexeme) :
                error_message = f"Procedimento {identificador.lexeme} já declarado"
                self.error(error_message)
                subroutine_declaration_node.add_child(Tree.TreeNode('<ERROR>', error_message))
            else:  
                subroutine_declaration_node.add_child(Tree.TreeNode(type="Terminal", value=identificador.lexeme)) 

        if identificador:
            self.sym_table.insert(name=identificador.lexeme, type='procedure', category="procedimento")

        self.sym_table.enter_scope()

        if self.current() and self.current().type == "abre_parentese":
            subroutine_declaration_node.add_child(self.parametros_formais())

        subroutine_declaration_node.add_child(self.match_node("ponto_virgula", {"identificador_tipo", "procedimento", "begin"}))

        subroutine_declaration_node.add_child(self.bloco())

        self.sym_table.exit_scope()

        return subroutine_declaration_node

    def parametros_formais(self):
        formal_parameters_node = Tree.TreeNode(type="<parametros_formais>")
        formal_parameters_node.add_child(self.match_node("abre_parentese", {"ponto_virgula", "variavel", "identificador", "fecha_parentese"}))

        formal_parameters_node.add_child(self.secao_parametros_formais())

        while self.current() and self.current().type == "ponto_virgula":
            formal_parameters_node.add_child(self.match_node("ponto_virgula", {"variavel", "identificador", "fecha_parentese"}))
            formal_parameters_node.add_child(self.secao_parametros_formais())

        formal_parameters_node.add_child(self.match_node("fecha_parentese", {"ponto_virgula"}))
        return formal_parameters_node
    
    def secao_parametros_formais(self):
        formal_parameter_section_node = Tree.TreeNode(type="<secao_parametros_formais>")

        if self.current().type == "variavel":
            formal_parameter_section_node.add_child(self.match_node("variavel", {"dois_pontos", "identificador_tipo", "ponto_virgula", "fecha_parentese"}))

        identifiers, variable_list_node = self.lista_identificadores()
        formal_parameter_section_node.add_child(variable_list_node)
    

        formal_parameter_section_node.add_child(self.match_node("dois_pontos", {"identificador_tipo", "ponto_virgula", "fecha_parentese"}))

        identificador_tipo, child = self.match_node("identificador_tipo", {"ponto_virgula", "fecha_parentese"}, flag_return_token=True)
        formal_parameter_section_node.add_child(child)

        self.fill_table(identifiers, identificador_tipo, "variável")

        return formal_parameter_section_node

    def comando_composto(self):
        compound_command_node = Tree.TreeNode(type="<comando_composto>")
        compound_command_node.add_child(self.match_node("begin", {"identificador", "identificador_procedimento", "if", "while", "begin", "ponto_virgula", "end"}))

        if self.current() and self.current().type != "end":
            compound_command_node.add_child(self.comando())

            while self.current() and self.current().type == "ponto_virgula":
                compound_command_node.add_child(self.match_node("ponto_virgula", {"identificador", "identificador_procedimento", "if", "while", "begin", "ponto_virgula", "end"}))
                compound_command_node.add_child(self.comando())

        compound_command_node.add_child(self.match_node("end", {"ponto", "ponto_virgula", "end", "else"}))
        return compound_command_node
    
    def comando(self):
        command_node = Tree.TreeNode(type="<comando>")
        token = self.current()

        if not token:
            return 
        
        if token.type == "end":
            return

        if token.type in ("identificador", "identificador_procedimento"):
            ident, child = self.match_node(token.type, {"if", "while", "begin", "abre_colchete", "fecha_colchete", "atribuicao", "abre_parentese", "fecha_parentese", "ponto_virgula", "end", "else"}, flag_return_token=True)
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
            ident_rest_node.add_child(self.match_node("abre_colchete", {"fecha_colchete", "atribuicao", "abre_parentese", "fecha_parentese", "ponto_virgula", "end", "else"}))
            
            ident_rest_node.add_child(self.expressao())
            ident_rest_node.add_child(self.match_node("fecha_colchete", {"atribuicao", "abre_parentese", "fecha_parentese", "ponto_virgula", "end", "else"}))
            token = self.current() 

        if token and token.type == "atribuicao":
            if ident:
                self.sym_table.add_reference(ident.lexeme)
            ident_rest_node.add_child(self.match_node("atribuicao", {"abre_parentese", "fecha_parentese", "ponto_virgula", "end", "else"}))
            ident_rest_node.add_child(self.expressao())

        elif token and token.type == "abre_parentese":
            if ident:
                self.sym_table.add_reference(ident.lexeme)
            ident_rest_node.add_child(self.match_node("abre_parentese", {"fecha_parentese", "ponto_virgula", "end", "else"}))
            if self.current() and self.current().type != "fecha_parentese":
                ident_rest_node.add_child(self.lista_expressoes())
            ident_rest_node.add_child(self.match_node("fecha_parentese", {"ponto_virgula", "end", "else"}))
            
        else:
            if ident:
                self.sym_table.add_reference(ident.lexeme)
                ident_rest_node.add_child(Tree.TreeNode(type="Terminal", value=ident.lexeme))
        
        return ident_rest_node

    def comando_condicional(self):
        sync_symbols_comando_condicional = {"operador_soma", "operador_subtracao", "operador_multiplicacao", "operador_divisao", "and", "numero_inteiro", "identificador_constante", "identificador", "abre_parentese", "fecha_parentese", "not", "or","relacao", "then", "identificador", "identificador_procedimento", "if", "while", "begin", "ponto_virgula", "end", "else"}

        conditional_command_node = Tree.TreeNode(type="<comando_condicional>")
        conditional_command_node.add_child(self.match_node("if", sync_symbols_comando_condicional))
        conditional_command_node.add_child(self.expressao())
        conditional_command_node.add_child(self.match_node("then", sync_symbols_comando_condicional - {"then"}))

        conditional_command_node.add_child(self.comando())

        if self.current() and self.current().type == "else":
            conditional_command_node.add_child(self.match_node("else", sync_symbols_comando_condicional - {"then"}))
            conditional_command_node.add_child(self.comando())

        return conditional_command_node

    def comando_repetitivo(self):
        sync_symbols_comando_repetitivo = {"do", "operador_soma", "operador_subtracao", "operador_multiplicacao", "operador_divisao", "and", "numero_inteiro", "identificador_constante", "identificador", "abre_parentese", "fecha_parentese", "not", "or", "relacao", "identificador", "identificador_procedimento", "if", "while", "begin", "ponto_virgula", "end", "else"}
        repetitive_command_node = Tree.TreeNode(type="<comando_repetitivo>")
        repetitive_command_node.add_child(self.match_node("while", sync_symbols_comando_repetitivo))
        repetitive_command_node.add_child(self.expressao())
        repetitive_command_node.add_child(self.match_node("do", sync_symbols_comando_repetitivo - {"do"}))
        repetitive_command_node.add_child(self.comando())
        return repetitive_command_node


    def lista_expressoes(self):
        expression_list_node = Tree.TreeNode(type="<lista_expressoes>")
        expression_list_node.add_child(self.expressao())

        while self.current() and self.current().type == "virgula":
            expression_list_node.add_child(self.match_node("virgula"), {"operador_soma", "operador_subtracao", "operador_multiplicacao", "operador_divisao", "and", "numero_inteiro", "identificador_constante", "identificador", "abre_parentese", "fecha_parentese", "not", "or", "relacao", "ponto_virgula", "end", "else"})
            expression_list_node.add_child(self.expressao())

        return expression_list_node

    def expressao(self):
        expression_node = Tree.TreeNode(type="<expressao>")
        expression_node.add_child(self.expressao_simples())

        if self.current() and self.current().type == "relacao":
            expression_node.add_child(self.match_node("relacao", {"operador_soma", "operador_subtracao", "operador_multiplicacao", "operador_divisao", "and", "numero_inteiro", "identificador_constante", "identificador", "abre_parentese", "fecha_parentese", "not", "or", "ponto_virgula", "end", "else", "then", "do", "fecha_parentese", "fecha_colchete", "virgula"}))
            expression_node.add_child(self.expressao_simples())
        
        return expression_node

    def expressao_simples(self):
        sync_symbols_expressao_simples = {"operador_multiplicacao", "operador_divisao", "and", "numero_inteiro", "identificador_constante", "identificador", "abre_parentese", "fecha_parentese", "not", "operador_soma", "operador_subtracao", "or", "relacao", "ponto_virgula", "end", "else", "then", "do", "fecha_parentese", "fecha_colchete", "virgula"}
        # Lida com o [+|-] opcional no início (Regra 18) 
        simple_expression_node = Tree.TreeNode(type="<expressao_simples>")

        if self.current() and self.current().type in ("operador_soma", "operador_subtracao"):
            simple_expression_node.add_child(self.match_node(self.current().type, sync_symbols_expressao_simples))
            # self.advance()

        simple_expression_node.add_child(self.termo())

        while self.current() and self.current().type in ("operador_soma", "operador_subtracao", "or"):
            simple_expression_node.add_child(self.match_node(self.current().type, sync_symbols_expressao_simples - {"operador_soma", "operador_subtracao", "or"}))
            # self.advance()
            simple_expression_node.add_child(self.termo())

        return simple_expression_node

    def termo(self):
        term_node = Tree.TreeNode(type="<termo>")
        term_node.add_child(self.fator())

        while self.current() and self.current().type in ("operador_multiplicacao", "operador_divisao", "and"):
            term_node.add_child(self.match_node(self.current().type, {"numero_inteiro", "identificador_constante", "identificador", "abre_colchete", "fecha_colchete", "abre_parentese", "fecha_parentese", "not", "operador_soma", "operador_subtracao", "or", "relacao", "ponto_virgula", "end", "else", "then", "do", "fecha_parentese", "fecha_colchete","virgula"}))
            # self.advance()
            term_node.add_child(self.fator())
        
        return term_node
    
    def fator(self):
        sync_symbols_fator = {"operador_multiplicacao", "operador_divisao", "and", "operador_soma", "operador_subtracao", "or", "relacao", "ponto_virgula", "end", "else", "then", "do", "fecha_parentese", "fecha_colchete","virgula"}

        factor_node = Tree.TreeNode(type="<fator>")
        token = self.current()

        if not token:
            self.error("Fim de arquivo inesperado")
            return
        
        if token.type == "numero_inteiro":
            factor_node.add_child(self.match_node("numero_inteiro", sync_symbols_fator | {"identificador_constante", "identificador", "abre_colchete", "fecha_colchete", "abre_parentese", "fecha_parentese", "not"}))

        elif token.type == "identificador_constante":
            factor_node.add_child(self.match_node("identificador_constante", sync_symbols_fator | {"identificador", "abre_colchete", "fecha_colchete", "abre_parentese", "fecha_parentese", "not"}))
        
        elif token.type == "identificador":
            ident = self.match("identificador", sync_symbols_fator | {"abre_colchete", "fecha_colchete", "abre_parentese", "fecha_parentese", "not"})
            if ident:
                self.sym_table.add_reference(ident.lexeme)
                factor_node.add_child(Tree.TreeNode(type="Terminal", value=ident.lexeme))
            
            if self.current() and self.current().type == "abre_colchete":
                factor_node.add_child(self.match_node("abre_colchete", sync_symbols_fator | {"fecha_colchete", "abre_parentese", "fecha_parentese", "not"}))
                factor_node.add_child(self.expressao())
                factor_node.add_child(self.match_node("fecha_colchete", sync_symbols_fator | {"abre_parentese", "fecha_parentese", "not"}))

        elif token.type == "abre_parentese":
            factor_node.add_child(self.match_node("abre_parentese", sync_symbols_fator | {"fecha_parentese", "not"}))
            factor_node.add_child(self.expressao())
            factor_node.add_child(self.match_node("fecha_parentese", sync_symbols_fator | {"not"}))
        
        elif token.type == "not":
            factor_node.add_child(self.match_node("not", sync_symbols_fator))
            factor_node.add_child(self.fator())

        else:
            self.error(f"Fator inesperado: {token.lexeme} Linha: {token.line}")
            factor_node.add_child(Tree.TreeNode('<ERROR>', f"Fator inesperado: {token.lexeme} Linha: {token.line}"))
            self.advance()
        
        return factor_node