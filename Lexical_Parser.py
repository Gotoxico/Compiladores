import re
from dataclasses import dataclass
from typing import Optional

def read_source(mode: str, content: str):
    mode = mode.lower()

    if mode == 'file':
        with open(content, 'r', encoding='utf-8') as f:
            return f.read()

    elif mode == 'sequence':
        return content

    else:
        raise ValueError("Opcao Invalida")



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
    ('numero_real', r'\d{1,10}\.\d{1,10}'),
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
    ('identificador_tipo', r'\bint\b|\breal\b|\bboolean\b'),
    ('identificador_procedimento', r'\bread\b|\bwrite\b'),
    ('identificador_constante', r'\btrue\b|\bfalse\b'),

    # Parênteses
    ('abre_parentese', r'\('),
    ('fecha_parentese', r'\)'),

    # Operadores
    ('operador_soma', r'\+'),
    ('operador_subtracao', r'-'),
    ('operador_multiplicacao', r'\*'),
    ('operador_divisao', r'/'),

    # Identificador genérico
    ('identificador', r'[A-Za-z_][A-Za-z0-9_]*'),

    # Controle
    ('NEWLINE', r'\n'),
    ('SKIP', r'[ \t]+'),

    ('MISMATCH', r'.'),
]

tok_regex = '|'.join(
    f'(?P<{name}>{pattern})'
    for name, pattern in token_specification
)



def lexico(sequence):
    line_num = 1
    line_start = 0

    for match in re.finditer(tok_regex, sequence):
        kind = match.lastgroup
        lexeme = match.group()
        start = match.start()
        end = match.end()

        if kind == 'NEWLINE':
            line_num += 1
            line_start = end
            continue

        if kind in ('SKIP', 'comentario_bloco', 'comentario_linha'):
            continue

        if kind in ('comentario_bloco_incompleto'):
            yield Token(kind)
            continue

        '''if kind == 'MISMATCH':
            raise RuntimeError(
                f'Caractere inesperado "{lexeme}" na linha {line_num}'
            )'''

        col_start = start - line_start + 1
        col_end = end - line_start

        yield Token(kind, lexeme, line_num, col_start, col_end)