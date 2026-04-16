import re
from dataclasses import dataclass
from typing import Optional

@dataclass
class Token:
    type: str
    lexeme: Optional[str] = None
    line: Optional[int] = None
    col_start: Optional[int] = None
    col_end: Optional[int] = None



token_specification = [
    # Comentários 
    ('comentario_bloco', r'\{[\s\S]*?\}'),
    ('comentario_bloco_incompleto', r'\{[\s\S]*$'),
    ('comentario_linha', r'//[^\n]*'),

    # Atribuição
    ('atribuicao', r':='),

    # Números 
    ('MISMATCH_numero_inteiro', r'\d{11,}'),
    ('numero_inteiro', r'\d{1,10}'),

    # Pontuação
    ('ponto', r'\.'),
    ('ponto_virgula', r';'),
    ('virgula', r','),
    ('dois_pontos', r':'),

    # Palavras reservadas
    ('programa', r'\bprogram\b'),
    ('procedimento', r'\bprocedure\b'),
    ('variavel', r'\bvar\b'),
    ('begin', r'\bbegin\b'),
    ('end', r'\bend\b'),
    ('if', r'\bif\b'),
    ('then', r'\bthen\b'),
    ('else', r'\belse\b'),
    ('while', r'\bwhile\b'),
    ('do', r'\bdo\b'),

    # Relações
    ('relacao', r'<>|<=|>=|=|<|>'),

    # Identificadores pré-declarados
    ('identificador_tipo', r'\bint\b|\bboolean\b'), 
    ('identificador_procedimento', r'\bread\b|\bwrite\b'),
    ('identificador_constante', r'\btrue\b|\bfalse\b'),

    # Parênteses
    ('abre_parentese', r'\('),
    ('fecha_parentese', r'\)'),

    # Colchetes
    ('abre_colchete', r'\['),
    ('fecha_colchete', r'\]'),

    # Operadores
    ('operador_soma', r'\+'),
    ('operador_subtracao', r'-'),
    ('operador_multiplicacao', r'\*'),
    ('operador_divisao', r'\bdiv\b'),

    # Operadores lógicos
    ('or', r'\bor\b'),
    ('and', r'\band\b'),

    # Identificador genérico
    ('MISMATCH_identificador', r'[A-Za-z_][A-Za-z0-9_]{10,}'),
    ('identificador', r'[A-Za-z_][A-Za-z0-9_]{0,9}'),

    # Controle
    ('NEWLINE', r'\n'),
    ('SKIP', r'[ \t]+'),

    ('MISMATCH', r'.'),
]



class lexer:
    def __init__(self):
        self.tok_regex_or_list = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)
        self.line_num = 1
        self.line_start = 0

    def analise(self, sequence):
        for match in re.finditer(self.tok_regex_or_list, sequence):
            kind = match.lastgroup
            lexeme = match.group()
            start = match.start()
            end = match.end()

            if kind == 'NEWLINE':
                self.line_num += 1
                self.line_start = end
                continue

            if kind in ('SKIP', 'comentario_bloco', 'comentario_linha'):
                # CONSERTO: Atualizar linhas consumidas pelo comentário de bloco
                if kind == 'comentario_bloco':
                    quebras = lexeme.count('\n')
                    if quebras > 0:
                        self.line_num += quebras
                        # Encontra a posição exata da última quebra de linha dentro do comentário
                        ultimo_newline = lexeme.rfind('\n')
                        self.line_start = start + ultimo_newline + 1
                continue

            if kind in ('comentario_bloco_incompleto'):
                yield Token(kind, None, self.line_num)
                continue

            '''if kind == 'MISMATCH':
                raise RuntimeError(
                    f'Caractere inesperado "{lexeme}" na linha {line_num}'
                )'''

            col_start = start - self.line_start + 1
            col_end = end - self.line_start

            yield Token(kind, lexeme, self.line_num, col_start, col_end)








